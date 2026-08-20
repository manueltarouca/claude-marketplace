#!/usr/bin/env python3
"""
Repair a skill-creator static review page whose embedded data contains HTML.

    python3 fix-review-html.py <review.html>

`generate_review.py` inlines each run's output into a JSON blob inside a
`<script>` tag. If any output contains the literal text `</script>` — which is
guaranteed for anything web-related, since an answer showing how to load an SDK
will quote a script tag — the HTML parser ends the block right there. The page
then renders the remainder of the JSON as text, which is the "gibberish at the
bottom", and the viewer's own JavaScript never runs at all.

The fix is the standard one: escape `</` as `<\\/` inside the embedded JSON.
`\\/` is a valid JSON escape for `/`, so the decoded string is byte-identical
and the page still displays `</script>` to the reader.
"""
import re
import sys
from pathlib import Path


def fix(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    fixed = 0

    for i, line in enumerate(lines):
        if "EMBEDDED_DATA" not in line:
            continue
        # The generator writes the whole JSON payload on one line, so the repair
        # is confined to it and cannot disturb the viewer's real script tags.
        count = line.count("</")
        if count:
            lines[i] = line.replace("</", "<\\/")
            fixed += count

    if fixed:
        path.write_text("\n".join(lines), encoding="utf-8")
    return fixed


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: fix-review-html.py <review.html>")
    target = Path(sys.argv[1])
    n = fix(target)
    print(f"escaped {n} occurrence(s) of '</' in the embedded data of {target.name}"
          if n else f"nothing to fix in {target.name}")
