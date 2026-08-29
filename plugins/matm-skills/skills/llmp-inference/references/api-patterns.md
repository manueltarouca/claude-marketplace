# API patterns against llmp

Base URL `http://127.0.0.1:4000/v1`, any API key. Python examples use the
`openai` package (`uv run --with openai python script.py`, or add it to the
project). Anything speaking the OpenAI wire protocol works the same way.

## Chat completions

```python
from openai import OpenAI
c = OpenAI(base_url="http://127.0.0.1:4000/v1", api_key="sk-local")
r = c.chat.completions.create(
    model="gpt-5.6-terra",
    messages=[{"role": "system", "content": "..."}, {"role": "user", "content": "..."}],
)
print(r.choices[0].message.content)
```

Streaming: `stream=True`, iterate `chunk.choices[0].delta.content`.

## Responses API (+ reasoning effort)

```python
r = c.responses.create(
    model="gpt-5.6-terra",
    instructions="You are ...",          # your persona; appended after the Codex base prompt
    input=[{"role": "user", "content": "..."}],
    reasoning={"effort": "low"},         # low|medium|high; low is fine for mechanical work
)
print(r.output_text)
```

## Structured output: forced function tool (the only enforced way)

`response_format` and `text.format` are dropped by the provider. A forced,
strict function call is honoured and returns exactly the schema:

```python
schema = {"type": "object", "additionalProperties": False,
          "required": ["items"],
          "properties": {"items": {"type": "array", "items": {
              "type": "object", "additionalProperties": False,
              "required": ["id", "en"],
              "properties": {"id": {"type": "string"}, "en": {"type": "string"}}}}}}

r = c.responses.create(
    model="gpt-5.6-terra",
    instructions="Translate JA→EN game strings. Keep {0}-style placeholders and tags verbatim.",
    input=[{"role": "user", "content": json.dumps(items, ensure_ascii=False)}],
    tools=[{"type": "function", "name": "submit", "strict": True, "parameters": schema}],
    tool_choice={"type": "function", "name": "submit"},
)
args = json.loads(next(o for o in r.output if o.type == "function_call").arguments)
```

Chat-completions equivalent: `tools=[{"type":"function","function":{"name":"submit","strict":True,"parameters":schema}}]`,
`tool_choice={"type":"function","function":{"name":"submit"}}`, read
`r.choices[0].message.tool_calls[0].function.arguments`.

Strict mode requires `additionalProperties: false` and every property listed
in `required` on every object.

## Image generation

```python
r = c.responses.create(
    model="gpt-5.6-luna",
    input=[{"role": "user", "content": "Generate an image of ... no text."}],
    tools=[{"type": "image_generation"}],
)
for o in r.output:
    if o.type == "image_generation_call" and o.result:
        open("out.png", "wb").write(base64.b64decode(o.result))
```

~25s per image, 1254×1254 PNG. `llmp image "prompt" -n name -o dir/` does the same from the shell.

## Concurrency and errors

- Subscription rate limits apply per account. Start with 4 parallel requests;
  back off on HTTP 429 (sleep 5s × attempt) and retry 5xx up to 3 times. The
  bundled `scripts/batch.py` implements this.
- A 500 with `Unknown items in responses API response` or an SSE body where
  JSON was expected means the proxy is running an old config without the
  LiteLLM patches: `llmp restart` (config lives at `~/.config/llmp/config.yaml`,
  it must list `litellm_proxy.patches.proxy_handler_instance` under callbacks).
- Requests carrying `max_tokens`/`metadata` are fine — the proxy strips them.
