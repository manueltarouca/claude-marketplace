#!/usr/bin/env python3
"""Resumable batch runner against the local llmp proxy. Stdlib only.

Reads JSONL items (each with an `id`), sends them in chunks to
/v1/responses with a forced strict function tool so every result matches
--schema, and appends results to an output JSONL. Ids already present in the
output are skipped, so re-running resumes.

    python3 batch.py --input items.jsonl --output out.jsonl \
        --system system.md --schema item_schema.json \
        [--model gpt-5.6-terra] [--chunk 30] [--concurrency 4] \
        [--reasoning low] [--limit N] [--base-url http://127.0.0.1:4000/v1]
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

TOOL_NAME = "submit"


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def done_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {str(r["id"]) for r in read_jsonl(path) if "id" in r}


def wrap_schema(item_schema: dict) -> dict:
    props = item_schema.get("properties", {})
    if "id" not in props:
        sys.exit("--schema must describe one item and include an `id` property")
    item = {
        **item_schema,
        "additionalProperties": False,
        "required": sorted(props),  # strict mode: every property required
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["items"],
        "properties": {"items": {"type": "array", "items": item}},
    }


def build_request(args, chunk: list[dict], schema: dict, system: str) -> bytes:
    body = {
        "model": args.model,
        "instructions": system,
        "input": [
            {
                "role": "user",
                "content": (
                    f"Process every item below and call `{TOOL_NAME}` once with one "
                    f"result per input id, in the same order.\n\n"
                    + json.dumps(chunk, ensure_ascii=False)
                ),
            }
        ],
        "tools": [{"type": "function", "name": TOOL_NAME, "strict": True, "parameters": schema}],
        "tool_choice": {"type": "function", "name": TOOL_NAME},
    }
    if args.reasoning:
        body["reasoning"] = {"effort": args.reasoning}
    return json.dumps(body, ensure_ascii=False).encode("utf-8")


def call(args, payload: bytes) -> list[dict]:
    req = urllib.request.Request(
        f"{args.base_url}/responses",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": "Bearer sk-local"},
    )
    last: Exception | None = None
    for attempt in range(1, args.retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=args.timeout) as r:
                data = json.load(r)
            for item in data.get("output", []):
                if item.get("type") == "function_call" and item.get("name") == TOOL_NAME:
                    return json.loads(item["arguments"])["items"]
            raise RuntimeError(f"no {TOOL_NAME} call in response: {json.dumps(data)[:400]}")
        except urllib.error.HTTPError as e:
            last = e
            body = e.read().decode(errors="replace")[:300]
            if e.code == 429 or e.code >= 500:
                time.sleep(5 * attempt)
                continue
            raise RuntimeError(f"HTTP {e.code}: {body}") from e
        except (urllib.error.URLError, TimeoutError, RuntimeError, KeyError, json.JSONDecodeError) as e:
            last = e
            time.sleep(2 * attempt)
    raise RuntimeError(f"gave up after {args.retries} attempts: {last}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--system", required=True, help="system prompt: a file path or literal text")
    p.add_argument("--schema", required=True, type=Path, help="JSON schema of ONE output item (must have `id`)")
    p.add_argument("--model", default="gpt-5.6-terra")
    p.add_argument("--chunk", type=int, default=30)
    p.add_argument("--concurrency", type=int, default=4)
    p.add_argument("--reasoning", choices=["low", "medium", "high"], default=None)
    p.add_argument("--limit", type=int, default=None, help="only process the first N pending items")
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--base-url", default="http://127.0.0.1:4000/v1")
    args = p.parse_args()

    system = Path(args.system).read_text(encoding="utf-8") if Path(args.system).is_file() else args.system
    schema = wrap_schema(json.loads(args.schema.read_text(encoding="utf-8")))

    items = read_jsonl(args.input)
    skip = done_ids(args.output)
    pending = [it for it in items if str(it["id"]) not in skip]
    if args.limit:
        pending = pending[: args.limit]
    chunks = [pending[i : i + args.chunk] for i in range(0, len(pending), args.chunk)]
    print(
        f"{len(items)} items, {len(skip)} already done, {len(pending)} pending in {len(chunks)} chunks "
        f"-> {args.model} x{args.concurrency}",
        file=sys.stderr,
    )
    if not chunks:
        return 0

    lock = threading.Lock()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out = args.output.open("a", encoding="utf-8")
    ok = failed = 0
    t0 = time.monotonic()

    def run(chunk: list[dict]) -> tuple[int, int]:
        expected = {str(it["id"]) for it in chunk}
        results = call(args, build_request(args, chunk, schema, system))
        got = 0
        with lock:
            for r in results:
                if str(r.get("id")) in expected:
                    out.write(json.dumps({"id": r["id"], **{k: v for k, v in r.items() if k != "id"}}, ensure_ascii=False) + "\n")
                    got += 1
            out.flush()
        return got, len(expected) - got

    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futures = {ex.submit(run, ch): ch for ch in chunks}
        for fut in as_completed(futures):
            ch = futures[fut]
            try:
                got, missing = fut.result()
                ok += got
                failed += missing
                if missing:
                    print(f"chunk starting {ch[0]['id']}: {missing} ids missing from output", file=sys.stderr)
            except Exception as e:  # noqa: BLE001 - report and keep going, resume handles the rest
                failed += len(ch)
                print(f"chunk starting {ch[0]['id']} failed: {e}", file=sys.stderr)
            print(f"  {ok} done, {failed} failed, {time.monotonic() - t0:.0f}s", file=sys.stderr, end="\r")

    out.close()
    print(f"\ndone: {ok} ok, {failed} failed, {time.monotonic() - t0:.0f}s, model={args.model} -> {args.output}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
