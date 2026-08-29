---
name: llmp-inference
description: Use the local `llmp` proxy (LiteLLM over the user's ChatGPT subscription, OpenAI-compatible at http://127.0.0.1:4000/v1, no API key) as the inference endpoint whenever a project needs to call an LLM from code rather than from a harness like Claude Code or Codex. Covers bringing the proxy up, model choice (gpt-5.6-sol/terra/luna), structured JSON output via forced function tools, and a bundled resumable batch runner. Reach for it for any scripted or bulk LLM work — batch translation/localization (e.g. Japanese game strings → English), classification, extraction, summarisation, tagging, data cleaning, synthetic data, LLM-as-judge, image generation from a script — and whenever the user asks for "an endpoint", "an API key for OpenAI/GPT", "which model should I use", or wants to automate inference without paying per token. Do NOT use for interactive chat or for work Claude itself should just do in this session.
---

# llmp-inference

`llmp` is a `uv` tool on this machine that runs a LiteLLM proxy backed by the
user's ChatGPT subscription (same OAuth login as Codex CLI). Any OpenAI client
pointed at `http://127.0.0.1:4000/v1` works; the API key is ignored. There is no
per-token cost — the constraints are subscription rate limits and latency.

Source: `~/code/projects/litellm-proxy` (README there has the details).

## Preflight (every session, ~2s)

```bash
llmp status || llmp up      # start if needed; prints health + token state
```

- `command not found` → `uv tool install --editable ~/code/projects/litellm-proxy`
- `auth: expired, run llmp login` → tell the user to run `llmp login` in their
  terminal (it is an interactive device-code flow; do not run it from a script).
- `llmp logs -n 50` when requests fail with 500s.

## Models

| model | use for |
|---|---|
| `gpt-5.6-terra` | default workhorse for bulk work: balanced quality/speed |
| `gpt-5.6-sol` | frontier: glossary/style-guide creation, the hard 10%, QA/judge passes |
| `gpt-5.6-luna` | fast: trivial items, first drafts, smoke tests |
| `chatgpt/<name>` | passthrough for anything else the backend serves (`chatgpt/gpt-5.5`) |

Since cost is not a factor, pick by quality-vs-latency only, and when unsure run
a 30–50 item sample through two models and let the user compare. Add
`reasoning={"effort": "low"}` (Responses API) for mechanical bulk tasks; it
noticeably cuts latency.

## Things that are different about this backend

- **Every call carries ~1.6k tokens of Codex system instructions** that the
  provider prepends (the backend expects them). Batch 20–50 items per request so
  the overhead is amortised, and put your own persona in `instructions` /
  system — the default framing is "coding agent", which shows in tone if you
  don't.
- **`response_format` / `text.format` are stripped** by the provider, so JSON
  mode and JSON-schema outputs are silently ignored. Use a **forced function
  tool with `strict: true`** instead — it is enforced and reliable
  (`scripts/batch.py` does this for you).
- `max_tokens`/`max_output_tokens` are stripped (backend rejects them). Control
  length in the prompt.
- Both `/v1/chat/completions` and `/v1/responses` work, streaming and not.
  Image generation is a Responses call with `tools=[{"type":"image_generation"}]`
  (no `/images` endpoint); `llmp image "…" -n name -o dir/` wraps that.

## Batch work: use the bundled runner

Do not hand-roll a batch loop; the runner already handles chunking,
concurrency, retries with backoff, strict-schema output, and resume:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/llmp-inference/scripts/batch.py" \
  --input items.jsonl --output out.jsonl \
  --system system.md --schema schema.json \
  --model gpt-5.6-terra --chunk 30 --concurrency 4 --reasoning low
```

- `items.jsonl`: one JSON object per line with an `id` plus whatever fields
  the prompt needs (`{"id":"ui_001","ja":"ガチャを10連で引く"}`).
- `schema.json`: JSON schema for **one output item**; it must contain `id`
  (the runner wraps it in `{"items": [...]}` and forces the tool call).
- `out.jsonl`: one result per line, `id` first. Re-running skips ids already
  present, so a killed run resumes where it stopped.
- Prints a summary line: items done, failures, elapsed, model.

Workflow that works well:

1. Look at a sample of the input and write `system.md` with: task, target
   audience/register, hard constraints (preserve `{0}`, `%s`, `<color>` tags,
   `\n`, string length hints), and a glossary of names/terms. For localisation
   ask `gpt-5.6-sol` to draft the glossary from a few hundred source strings first.
2. Run 30–50 items with `--limit 50`, show the user a side-by-side, adjust the
   prompt. Only then run the whole set.
3. Optionally a second pass with `gpt-5.6-sol` as judge/fixer on flagged items
   (a `--schema` with a `confidence` or `needs_review` field makes flagging easy).

For one-off structured calls from your own code, read
`references/api-patterns.md` (OpenAI SDK snippets for chat, responses, forced
tool output, streaming, image generation, concurrency/retry guidance).
