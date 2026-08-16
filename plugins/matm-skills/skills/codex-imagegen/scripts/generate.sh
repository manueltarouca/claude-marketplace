#!/usr/bin/env bash
# Generate image variants via Codex CLI's built-in image_generation tool.
#
# Usage: generate.sh "<prompt>" <name> [count] [outdir]
#
#   prompt  What to draw.
#   name    Basename for outputs: <outdir>/<name>-1.png, <name>-2.png, ...
#   count   Number of variants (default 3). Runs in parallel.
#   outdir  Output directory (default generated/), relative to the CWD.
#
# Env:
#   EINK=1        Append 6-color e-paper palette guidance to the prompt.
#   ASPECT=...    Override the aspect/orientation instruction (default: 5:3 landscape).
#   REF=a.png[:b.png...]  Attach one or more reference images (colon-separated,
#                 PATH-style); generations must match them. With multiple refs,
#                 say in the prompt what each attached image is for.
#   CODEX_MODEL   Override the model passed to codex exec.
set -euo pipefail

PROMPT=${1:?usage: generate.sh "<prompt>" <name> [count] [outdir]}
NAME=${2:?missing output basename}
COUNT=${3:-3}
OUTDIR=${4:-generated}

ROOT="$(pwd)"
mkdir -p "$ROOT/$OUTDIR"

# Optional: steer generations toward art that survives reduction to a 6-color
# e-paper palette (black/white/red/yellow/green/blue) after dithering.
EINK_HINT="Style constraints: bold flat colors dominated by black, white, red, yellow, green and blue; high contrast; crisp shapes; avoid subtle gradients and muted pastel tones. The image will be shown on a 6-color e-paper display."
[ "${EINK:-0}" != "1" ] && EINK_HINT=""

ASPECT_HINT=${ASPECT:-"Landscape orientation, target aspect ratio 5:3 (it will be resized to 800x480)."}

MODEL_ARGS=()
[ -n "${CODEX_MODEL:-}" ] && MODEL_ARGS=(-m "$CODEX_MODEL")

REF_ARGS=()
REF_HINT=""
if [ -n "${REF:-}" ]; then
  # Colon-separated list; each becomes its own --image=. Single-token form:
  # -i/--image is multi-value and would swallow the positional prompt.
  IFS=':' read -r -a _refs <<< "$REF"
  for _r in "${_refs[@]}"; do
    [ -n "$_r" ] || continue
    [ -f "$_r" ] || { echo "ERROR: REF image not found: $_r" >&2; exit 2; }
    REF_ARGS+=(--image="$_r")
  done
  if [ "${#_refs[@]}" -gt 1 ]; then
    REF_HINT="${#_refs[@]} reference images are attached (in the order listed in the brief). Match the designs, characters and visual elements they establish EXACTLY — same faces, proportions, outfits and colors for any recurring character; same design language for any object or style reference. Only pose, expression, composition and art style may differ as instructed. The brief states what each reference is for."
  else
    REF_HINT="A reference image of the canonical recurring character is attached. The character in your generated image MUST match that reference exactly: same face, hairstyle, body proportions, outfit and outfit colors — only the pose, expression and art style may differ as instructed."
  fi
fi

pids=()
for i in $(seq 1 "$COUNT"); do
  out="$OUTDIR/$NAME-$i.png"
  log="$ROOT/$OUTDIR/$NAME-$i.log"
  task="Use your image generation tool to create one image, then save it to '$out' (relative to the workspace root) as a PNG. $ASPECT_HINT

Subject: $PROMPT

$EINK_HINT

$REF_HINT

This is variant $i of $COUNT generated from the same brief — pick a distinct composition or interpretation so variants differ from each other. Do not create any other files. When done, reply with just the output path."
  echo "[$i/$COUNT] generating -> $out"
  codex exec \
    -s workspace-write \
    --skip-git-repo-check \
    -C "$ROOT" \
    --color never \
    ${MODEL_ARGS[@]+"${MODEL_ARGS[@]}"} \
    ${REF_ARGS[@]+"${REF_ARGS[@]}"} \
    "$task" >"$log" 2>&1 &
  pids+=($!)
done

fail=0
for idx in "${!pids[@]}"; do
  i=$((idx + 1))
  if ! wait "${pids[$idx]}"; then
    echo "ERROR: variant $i failed — see $OUTDIR/$NAME-$i.log" >&2
    fail=1
    continue
  fi
  if [ ! -s "$ROOT/$OUTDIR/$NAME-$i.png" ]; then
    echo "ERROR: variant $i produced no file — see $OUTDIR/$NAME-$i.log" >&2
    fail=1
  else
    rm -f "$ROOT/$OUTDIR/$NAME-$i.log"
    echo "[$i/$COUNT] done: $OUTDIR/$NAME-$i.png"
  fi
done
exit $fail
