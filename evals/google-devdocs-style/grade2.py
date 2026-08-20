#!/usr/bin/env python3
"""Grader for iteration 2.

Iteration 1 measured things Claude already does when you ask it to clean prose up,
so with_skill and baseline tied. These assertions target the choices the skill makes
that a general "write the docs" prompt does not: imperative headings over gerunds,
code font reserved for literals and bold for UI, conditions before instructions, the
Optional: prefix, and positive error phrasing.

For the two "add to an existing file" evals, only the added lines are graded. The
input is already in house style, so grading the whole file would score the fixture.
"""
import difflib
import json
import re
import sys
from pathlib import Path

PROPER = {"Phaser", "Vite", "Vitest", "Node", "CI", "TypeScript", "README", "ESLint",
          "Wasteland", "Kings", "Betty", "API", "CLI", "GPU", "YAML", "JSON", "npm",
          "itch.io", "Optional", "I", "BUTLER_API_KEY", "GitHub", "Actions"}

GERUNDS = {"getting", "running", "installing", "building", "deploying", "testing",
           "contributing", "configuring", "setting", "using", "starting", "adding",
           "developing", "publishing", "releasing"}

FILLER = ["simply", "easily", "obviously", "in order to", "utilize", "e.g.", "i.e.",
          "note that", "please note", "of course", "just"]


def headings(t):
    return re.findall(r"^#{1,6}\s+(.+)$", t, re.M)


def added_lines(original, new):
    diff = difflib.unified_diff(original.splitlines(), new.splitlines(), n=0, lineterm="")
    return "\n".join(l[1:] for l in diff if l.startswith("+") and not l.startswith("+++"))


def check(name, passed, evidence):
    return {"text": name, "passed": bool(passed), "evidence": evidence}


def sentence_case(t):
    bad = []
    for h in headings(t):
        words = re.findall(r"[A-Za-z][A-Za-z0-9'\.]*", h)
        caps = [w for w in words[1:] if w[0].isupper() and w not in PROPER]
        if caps:
            bad.append(f"{h!r}->{caps}")
    return bad


def gerund_headings(t):
    bad = []
    for h in headings(t):
        w = re.match(r"([A-Za-z]+)", h)
        if w and w.group(1).lower() in GERUNDS:
            bad.append(h)
    return bad


def trailing_conditions(t):
    """Imperative sentences that bury the condition at the end."""
    out = []
    for s in re.split(r"(?<=[.!?])\s+", t):
        s = s.strip()
        if re.match(r"^(Run|Pass|Set|Add|Use|Install|Deploy|Push|Build)\b", s) and \
           re.search(r"\bif\b", s, re.I):
            out.append(s[:90])
    return out


def grade_readme(t, _orig=None):
    out = []
    bad = sentence_case(t)
    out.append(check("All headings use sentence case", not bad,
                     "clean" if not bad else "; ".join(bad)))

    ger = gerund_headings(t)
    out.append(check("Task headings use imperative verbs, not gerunds ('Get started' not 'Getting started')",
                     not ger, "clean" if not ger else f"gerund headings: {ger}"))

    hits = [w for w in FILLER if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", t, re.I)]
    out.append(check("No filler or belittling words", not hits,
                     "clean" if not hits else f"found: {hits}"))

    we = len(re.findall(r"(?<![a-z])(we|our|us)(?![a-z])", t, re.I))
    out.append(check("Second person, no 'we'", we == 0, f"'we/our/us' count: {we}"))

    fut = re.findall(r"\bwill (?:be |only |also )?[a-z]+", t, re.I)
    out.append(check("Present tense, not future", not fut,
                     "clean" if not fut else f"found: {fut}"))

    bold_paths = re.findall(r"\*\*[^*]*(?:src/|\.ts|npm |package\.json)[^*]*\*\*", t)
    code_paths = len(re.findall(r"`[^`]*(?:src/|\.ts|npm |package\.json)[^`]*`", t))
    out.append(check("Literals in code font, bold not used for paths or commands",
                     not bold_paths and code_paths > 0,
                     f"code-font literals: {code_paths}, bolded literals: {len(bold_paths)}"))

    tc = trailing_conditions(t)
    out.append(check("Conditions come before instructions", not tc,
                     "clean" if not tc else f"trailing condition: {tc}"))

    facts = ["npm run dev", "npm test", "npm run build", "npm run lint", "5173",
             "20", "Phaser", "Vite", "src/scenes", "src/entities", "src/systems"]
    missing = [f for f in facts if f.lower() not in t.lower()]
    out.append(check("Covers the real project facts from package.json and the src tree",
                     not missing, "all present" if not missing else f"missing: {missing}"))
    return out


def grade_added_section(t, orig):
    add = added_lines(orig, t)
    out = []
    out.append(check("Existing content left intact",
                     all(l in t for l in orig.splitlines() if l.strip()),
                     "intact" if all(l in t for l in orig.splitlines() if l.strip())
                     else "existing lines changed or dropped"))

    bad = sentence_case(add)
    out.append(check("New heading uses sentence case", not bad,
                     "clean" if not bad else "; ".join(bad)))

    ger = gerund_headings(add)
    out.append(check("New heading uses an imperative verb, not a gerund", not ger,
                     "clean" if not ger else f"gerund: {ger}"))

    hits = [w for w in FILLER if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", add, re.I)]
    out.append(check("No filler in the added text", not hits,
                     "clean" if not hits else f"found: {hits}"))

    we = len(re.findall(r"(?<![a-z])(we|our|us)(?![a-z])", add, re.I))
    out.append(check("Added text uses second person, not 'we'", we == 0, f"'we/our/us': {we}"))

    fut = re.findall(r"\bwill (?:be |only |also )?[a-z]+", add, re.I)
    out.append(check("Added text uses present tense", not fut,
                     "clean" if not fut else f"found: {fut}"))

    opt = re.search(r"Optional:", add)
    out.append(check("Manual deploy marked with the 'Optional:' prefix", bool(opt),
                     "present" if opt else "no Optional: prefix on the by-hand path"))

    tc = trailing_conditions(add)
    out.append(check("Conditions come before instructions", not tc,
                     "clean" if not tc else f"trailing condition: {tc}"))

    facts = ["butler", "itch.io", "BUTLER_API_KEY", "tag", "butler push dist matm/betty:web"]
    missing = [f for f in facts if f.lower() not in add.lower()]
    out.append(check("States every fact given in the request", not missing,
                     "all present" if not missing else f"missing: {missing}"))
    return out


def grade_added_errors(t, orig):
    add = added_lines(orig, t)
    out = []
    keys = ["atlasTooBig", "badChannel"]
    out.append(check("Adds both keys with the requested names",
                     all(k in t for k in keys),
                     f"present: {[k for k in keys if k in t]}"))

    old_keys = ["missingConfig", "badYaml", "noAssetDir", "authExpired", "writeFailed",
                "spriteMissing", "quotaHit"]
    kept = [k for k in old_keys if k in t]
    out.append(check("Leaves the existing entries unchanged", len(kept) == len(old_keys),
                     f"kept {len(kept)}/{len(old_keys)}"))

    msgs = [m for m in re.findall(r'"((?:[^"\\]|\\.)*)"|`((?:[^`\\]|\\.)*)`', add)]
    msgs = [a or b for a, b in msgs]
    msgs = [m for m in msgs if len(m) > 15]

    bang = [m for m in msgs if "!" in m]
    out.append(check("No exclamation points", not bang, "clean" if not bang else f"{bang}"))

    neg = [m for m in msgs if re.search(r"^(Failed to|Could not|Unable to|Cannot)", m)]
    out.append(check("Positive phrasing ('Can't' / states the condition) over 'Failed to'",
                     not neg, "clean" if not neg else f"found: {neg}"))

    ableist = [m for m in msgs if re.search(r"\babort|sanity check|insane|\bkill\b", m, re.I)]
    out.append(check("No violent or ableist terms", not ableist,
                     "clean" if not ableist else f"{ableist}"))

    action = r"(reduce|split|lower|resize|increase|use|pass|set|choose|pick|change|" \
             r"rerun|run|shrink|remove|specify|select)"
    acted = [m for m in msgs if re.search(r"(?<![a-z])" + action + r"(?![a-z])", m, re.I)]
    out.append(check("Both messages tell the reader what to do next",
                     len(msgs) and len(acted) == len(msgs),
                     f"{len(acted)}/{len(msgs)} name a next step"))

    specific = re.search(r"4096", add) and re.search(r"web.{0,20}windows.{0,20}mac", add, re.I)
    out.append(check("Names the concrete limit (4096) and the valid channels",
                     bool(specific),
                     f"4096: {bool(re.search(r'4096', add))}, channel list: "
                     f"{bool(re.search(r'web.{0,20}windows.{0,20}mac', add, re.I))}"))
    return out


GRADERS = {
    "eval-3-readme-from-scratch": ("README.md", None, grade_readme),
    "eval-4-add-deploy-section": ("betty-docs.md", "inputs2/betty-docs.md", grade_added_section),
    "eval-5-add-error": ("errors.ts", "inputs2/errors-clean.ts", grade_added_errors),
}


def main(root, base):
    root, base = Path(root), Path(base)
    summary = {}
    for d, (fname, orig_rel, fn) in GRADERS.items():
        orig = (base / orig_rel).read_text() if orig_rel else None
        for run in ("with_skill", "without_skill"):
            p = root / d / run / "outputs" / fname
            if not p.exists():
                print(f"MISSING {p}")
                continue
            exps = fn(p.read_text(encoding="utf-8", errors="replace"), orig)
            ok = sum(1 for e in exps if e["passed"])
            (p.parent.parent / "grading.json").write_text(json.dumps(
                {"expectations": exps, "passed": ok, "total": len(exps),
                 "pass_rate": round(ok / len(exps), 3)}, indent=2))
            summary[f"{d}/{run}"] = (ok, len(exps))
    print(f"\n{'eval':<32} {'with skill':>12} {'baseline':>12}")
    print("-" * 58)
    tw = bw = tt = 0
    for d in GRADERS:
        w, b = summary.get(f"{d}/with_skill"), summary.get(f"{d}/without_skill")
        if not w or not b:
            continue
        print(f"{d:<32} {w[0]:>7}/{w[1]:<4} {b[0]:>7}/{b[1]:<4}")
        tw += w[0]; bw += b[0]; tt += w[1]
    print("-" * 58)
    print(f"{'TOTAL':<32} {tw:>7}/{tt:<4} {bw:>7}/{tt:<4}")
    if tt:
        print(f"\nwith skill: {tw/tt:.0%}    baseline: {bw/tt:.0%}    delta: {(tw-bw)/tt:+.0%}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ".")
