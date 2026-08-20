#!/usr/bin/env python3
"""Mechanical grader for the google-devdocs-style evals.

Every assertion here is objectively checkable from the output text, so the same
script grades with_skill and without_skill runs identically. Judgement calls
(does this error message actually help?) are left to the human review pass.
"""
import json
import re
import sys
from pathlib import Path

# Words that are capitalised mid-heading legitimately.
PROPER = {
    "Phaser", "Vite", "Vitest", "Node", "CI", "TypeScript", "README", "PR", "PRs",
    "YAML", "CLI", "API", "JSON", "Betty", "Wasteland", "Kings", "Claude", "I",
    "GitHub", "npm", "itch.io", "Optional",
}

FILLER = ["simply", "easily", "obviously", "in order to", "utilize", "utilise",
          "e.g.", "i.e.", "note that", "please note", "of course"]


def headings(text):
    return re.findall(r"^#{1,6}\s+(.+)$", text, re.M)


def title_case_offenders(text):
    bad = []
    for h in headings(text):
        words = re.findall(r"[A-Za-z][A-Za-z0-9'\.]*", h)
        if len(words) < 2:
            continue
        caps = [w for w in words[1:] if w[0].isupper() and w not in PROPER]
        if caps:
            bad.append(f"{h!r} -> {caps}")
    return bad


def find_words(text, words):
    hits = []
    low = text.lower()
    for w in words:
        if re.search(r"(?<![a-z])" + re.escape(w.lower()) + r"(?![a-z])", low):
            hits.append(w)
    return hits


def strings_in(text):
    """Every quoted string literal, for the errors.ts eval."""
    return re.findall(r'"((?:[^"\\]|\\.)*)"|`((?:[^`\\]|\\.)*)`', text)


def flat_strings(text):
    return [a or b for a, b in strings_in(text)]


def check(name, passed, evidence):
    return {"text": name, "passed": bool(passed), "evidence": evidence}


def grade_readme(text):
    out = []
    bad = title_case_offenders(text)
    out.append(check("All headings use sentence case", not bad,
                     "clean" if not bad else "; ".join(bad)))

    hits = find_words(text, FILLER + ["just"])
    out.append(check("No filler or belittling words (simply, just, easily, in order to, utilize, e.g., note that)",
                     not hits, "clean" if not hits else f"found: {hits}"))

    we = len(re.findall(r"(?<![a-z])(we|our|us)(?![a-z])", text, re.I))
    out.append(check("Addresses the reader in second person rather than 'we'",
                     we == 0, f"'we/our/us' count: {we}"))

    ch = re.search(r"click here|read more|learn more here", text, re.I)
    out.append(check("No vague link text ('click here')", not ch,
                     "clean" if not ch else ch.group(0)))

    fut = re.findall(r"\bwill (?:be |only |also )?[a-z]+", text, re.I)
    out.append(check("Uses present tense, not future ('will be generated')",
                     not fut, "clean" if not fut else f"found: {fut}"))

    facts = ["npm install", "npm run dev", "npm test", "SKIP_ASSETS", "--filter",
             "src/scenes", "src/entities", "src/systems", "Vitest", "coverage/", "20"]
    missing = [f for f in facts if f.lower() not in text.lower()]
    out.append(check("Preserves every technical fact (commands, env var, flags, layout, Node version)",
                     not missing, "all present" if not missing else f"missing: {missing}"))
    return out


ACTION = r"(add|set|run|check|quote|remove|provide|create|sign in|reduce|update|verify|" \
         r"pass|specify|install|rename|delete|increase|reauthenticate|retry|use|move|" \
         r"split|reduce|configure|point|choose|fix|see|wait)"


def grade_errors(text):
    out = []
    keys = ["missingConfig", "badYaml", "noAssetDir", "atlasTooBig", "badChannel",
            "authExpired", "writeFailed", "spriteMissing", "quotaHit",
            "sanityCheckFailed", "startup", "packing", "done", "retry"]
    missing = [k for k in keys if k not in text]
    out.append(check("Keeps every exported key and the file's TypeScript shape",
                     not missing, "all present" if not missing else f"missing: {missing}"))

    msgs = flat_strings(text)
    bang = [m for m in msgs if "!" in m]
    out.append(check("No exclamation points in messages", not bang,
                     "clean" if not bang else f"found: {bang}"))

    blame = [m for m in msgs if re.search(r"you failed|you did not|your fault|you forgot", m, re.I)]
    out.append(check("Does not blame the reader", not blame,
                     "clean" if not blame else f"found: {blame}"))

    sorry = [m for m in msgs if re.search(r"\boops\b|\bsorry\b|unfortunately", m, re.I)]
    out.append(check("No apologies or 'Oops'", not sorry,
                     "clean" if not sorry else f"found: {sorry}"))

    dbl = [m for m in msgs if re.search(r"\bnot not\b|could not not", m, re.I)]
    out.append(check("No double negatives", not dbl,
                     "clean" if not dbl else f"found: {dbl}"))

    ableist = [m for m in msgs if re.search(r"sanity check|insane|\babort", m, re.I)]
    out.append(check("Replaces violent or ableist terms (sanity check, insane, abort)",
                     not ableist, "clean" if not ableist else f"found: {ableist}"))

    errs = [m for m in msgs if len(m) > 12]
    actionable = [m for m in errs if re.search(r"(?<![a-z])" + ACTION + r"(?![a-z])", m, re.I)]
    ratio = f"{len(actionable)}/{len(errs)} substantive messages name a next step"
    out.append(check("Most messages tell the reader what to do next (>=70%)",
                     len(errs) and len(actionable) / len(errs) >= 0.7, ratio))
    return out


def grade_claude_md(text):
    out = []
    bad = title_case_offenders(text)
    out.append(check("All headings use sentence case", not bad,
                     "clean" if not bad else "; ".join(bad)))

    hits = find_words(text, FILLER + ["just"])
    out.append(check("No filler or belittling words", not hits,
                     "clean" if not hits else f"found: {hits}"))

    dated = find_words(text, ["currently", "at this time", "for now", "right now"])
    novelty = re.findall(r"\b(?:is|which is|the) new\b", text, re.I)
    out.append(check("Timeless: no 'currently', 'at this time', or 'new' as novelty",
                     not dated and not novelty,
                     "clean" if not dated and not novelty else f"found: {dated + novelty}"))

    ch = re.search(r"click here|for more info", text, re.I)
    out.append(check("No vague link text", not ch, "clean" if not ch else ch.group(0)))

    rules = {
        "test-before-commit": r"test.{0,40}before.{0,20}commit|before.{0,20}commit.{0,40}test",
        "no-direct-main": r"main",
        "no-any-types": r"`?any`?",
        "dev-command": r"npm run dev",
        "port-5173": r"5173",
        "port-flag": r"--port",
        "test-command": r"npm test",
        "vitest": r"Vitest",
        "scenes-dir": r"src/scenes",
        "entities-dir": r"src/entities",
        "dialogue-dir": r"src/dialogue",
        "butler": r"butler",
    }
    missing = [k for k, pat in rules.items() if not re.search(pat, text, re.I)]
    out.append(check("Preserves every rule and technical fact", not missing,
                     "all present" if not missing else f"missing: {missing}"))
    return out


GRADERS = {
    "eval-0-readme-rewrite": ("README.md", grade_readme),
    "eval-1-error-messages": ("errors.ts", grade_errors),
    "eval-2-agent-instructions": ("CLAUDE.md", grade_claude_md),
}


def main(root):
    root = Path(root)
    summary = {}
    for eval_dir, (fname, fn) in GRADERS.items():
        for run in ("with_skill", "without_skill"):
            path = root / eval_dir / run / "outputs" / fname
            if not path.exists():
                print(f"MISSING {path}")
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            exps = fn(text)
            passed = sum(1 for e in exps if e["passed"])
            grading = {"expectations": exps,
                       "passed": passed, "total": len(exps),
                       "pass_rate": round(passed / len(exps), 3)}
            (path.parent.parent / "grading.json").write_text(json.dumps(grading, indent=2))
            summary[f"{eval_dir}/{run}"] = (passed, len(exps))
    print(f"\n{'eval':<34} {'with skill':>12} {'baseline':>12}")
    print("-" * 60)
    tw = bw = tt = 0
    for eval_dir in GRADERS:
        w = summary.get(f"{eval_dir}/with_skill")
        b = summary.get(f"{eval_dir}/without_skill")
        if not w or not b:
            continue
        print(f"{eval_dir:<34} {w[0]:>7}/{w[1]:<4} {b[0]:>7}/{b[1]:<4}")
        tw += w[0]; bw += b[0]; tt += w[1]
    print("-" * 60)
    print(f"{'TOTAL':<34} {tw:>7}/{tt:<4} {bw:>7}/{tt:<4}")
    if tt:
        print(f"\nwith skill: {tw/tt:.0%}    baseline: {bw/tt:.0%}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
