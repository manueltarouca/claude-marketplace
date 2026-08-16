---
name: codex-imagegen
description: Generate images locally via the Codex CLI's built-in image_generation tool — no API keys, uses the user's existing ChatGPT/Codex login. Produces N parallel variants per prompt, keeps a recurring character consistent across generations by attaching a reference image, and supports aspect-ratio and restricted-palette (e-ink) guidance. Use this whenever the user asks to generate, create, or iterate on images, sprites, game assets, wallpapers, illustrations, concept art, mascots, avatars, character sheets, or visual variants — especially "generate a few options", "make variants", "same character but…", or any mention of codex for images. Do NOT use for technical diagrams/flowcharts (draw those as SVG/mermaid) or when the user explicitly wants a different provider's API.
---

# codex-imagegen

Generate images through the locally installed Codex CLI. Each generation is a
non-interactive `codex exec` session that calls its `image_generation` tool and
saves a PNG into the workspace. Nothing leaves the machine except the prompt
(and optional reference image) going to the user's own Codex account — no API
keys to configure.

## Requirements (check once per session)

- `codex` on PATH and authenticated: `codex login status` → "Logged in".
- The `image_generation` feature enabled: `codex features list | grep image_generation`
  → `stable true`. If missing, tell the user to update Codex CLI.

## Generating

Use the bundled script — do not hand-roll `codex exec` calls; the script
handles sandboxing, prompt plumbing, parallelism, output verification and
failure logs:

```bash
"${CLAUDE_PLUGIN_ROOT}/skills/codex-imagegen/scripts/generate.sh" "<prompt>" <name> [count] [outdir]
```

- Outputs land as `<outdir>/<name>-<i>.png` (outdir defaults to `generated/`,
  created relative to the current directory).
- `count` variants run in PARALLEL (each is an independent codex session,
  ~30–90s; they draw on the user's Codex quota — mention this for large
  batches, and batch in groups of ≤10).
- Each variant's prompt gets an automatic "variant i of N — pick a distinct
  interpretation" nudge, so same-prompt variants genuinely differ.
- On failure the script leaves `<outdir>/<name>-<i>.log` — read it; the most
  common causes are auth expiry and quota exhaustion.
- Always verify results with `file` and by Reading the image before declaring
  success; generation can succeed as a process but miss the brief.

### Environment knobs

| Env | Effect |
|---|---|
| `ASPECT="..."` | Override the aspect instruction (default: landscape 5:3). E.g. `ASPECT="Square image. The subject must fill most of the frame."` |
| `REF=a.png[:b.png...]` | Attach one or more reference images (colon-separated, PATH-style); the prompt is augmented to match their characters/designs exactly. With multiple refs, state in the prompt what each attached image establishes ("first image: the hero's design; second image: the villain's design"). See "Consistent characters". |
| `EINK=1` | Append 6-color e-paper palette guidance (bold flat colors, black/white/red/green/blue/yellow, no subtle gradients). Off by default. |
| `CODEX_MODEL=...` | Override the codex model. |

## Prompt craft (learned the hard way)

- **Ban text**: always append "No text anywhere in the image" — generated text
  garbles, and real text should be composited programmatically afterwards.
- Structure prompts as: subject + action/scene + explicit art style + palette
  or mood constraints + composition note.
- Name a concrete art style or game aesthetic ("in the style of Dead Cells /
  Papers, Please / low-poly Polytopia") — this steers far more reliably than
  adjectives alone.
- For sprites to composite later, request "one solid uniform pure magenta
  background (RGB 255,0,255), no shadow, no border" — magenta chroma-keys
  cleanly to transparency.
- For a picking session, run distinct *themed* prompts in parallel (one call
  per theme) rather than N variants of one prompt; then let the user choose.

## Consistent characters (the reference-sheet pattern)

To keep the same character recognizable across many images and styles:

1. Lock a short text spec of the character (3–5 visual anchors — glasses,
   hair, signature item…). Paste it into every prompt.
2. Generate a **model sheet** once: "the SAME character three times side by
   side — front view, side profile, action pose; plain white background; no
   text". Have the user pick the canon sheet.
3. Pass that sheet to every subsequent generation via `REF=`. The script
   attaches it (`--image=` single-token form — the multi-value `-i` flag would
   swallow the prompt argument) and instructs the model to match face and
   design exactly while pose/style vary.
4. For gradual transformations (level-ups, aging, outfit arcs), **edit-chain**:
   generate stage N with `REF=` pointing at stage N-1's sheet, changing only
   the delta ("same face, now add …"). Faces stay stable; gear evolves.
5. Curate: view every output and regenerate off-model results — consistency
   comes from reference + curation, not reference alone.
6. Multiple references compose: attach several sheets at once
   (`REF=hero.png:villain.png:artifact.png`) for multi-character scenes, or a
   character sheet plus a style/scene reference. Attachment order matters only
   through your prompt — always spell out which image establishes what.

## Aftercare

The script produces raw PNGs at whatever size the model chose. Downstream
steps that commonly follow (resizing, palette quantization/dithering for
constrained displays, chroma-key transparency, contact sheets for side-by-side
review) are ordinary Pillow work — do them with `uv run --with pillow python`
one-offs sized to the task. When quantizing to a fixed palette, resize FIRST,
then dither (dither patterns don't survive scaling).
