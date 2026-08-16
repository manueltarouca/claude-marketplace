# matm — a personal Claude Code marketplace

My own skills, plus third-party skill collections tracked **live from their upstream
repos** rather than copied in. Upstream stays the source of truth; `claude plugin
update <plugin>@matm` pulls new commits.

## Install

```bash
claude plugin marketplace add manueltarouca/claude-marketplace
claude plugin install matm-skills@matm -s user -y
claude plugin install elevenlabs@matm  -s user -y
claude plugin install phaser@matm      -s project -y   # run inside a game project
```

## Plugins

| Plugin | Source | Skills | Notes |
|---|---|---|---|
| `matm-skills` | this repo, `plugins/matm-skills` | `codex-imagegen` | Image generation via the local Codex CLI — no API keys |
| `phaser` | `phaserjs/phaser` → `skills/` (sparse) | 28 | Phaser 4. ~3.2k always-on tokens, so enable per-project |
| `elevenlabs` | `elevenlabs/skills` | 10 | TTS, music, SFX, dubbing, STT, voice changer/isolator. Needs `ELEVENLABS_API_KEY` |

## Why sparse sources

Phaser's repo is ~470 MB, but its skills live in one `skills/` subdirectory. The
`git-subdir` source type sparse-clones just that path (~640 KB), so tracking upstream
costs nothing. Neither upstream repo ships a `.claude-plugin/plugin.json`, so those
entries set `"skills": "./"` and `"strict": false` — the marketplace entry is the whole
plugin definition.

## Adding a plugin

- **Upstream skills at the repo root** — `{"source": "github", "repo": "owner/repo"}` plus
  `"skills": "./"` and `"strict": false`.
- **Upstream skills in a subdirectory** — `{"source": "git-subdir", "url": "...", "path": "skills"}`,
  same two fields. Sparse-clones only that path.
- **My own** — add `plugins/matm-skills/skills/<name>/SKILL.md`; it ships with the plugin
  already listed. Reference bundled files with `${CLAUDE_PLUGIN_ROOT}`.

Then `claude plugin validate .` before pushing.

## Token cost

`claude plugin details <plugin>` reports the always-on cost a plugin adds to every
session. Check it before enabling anything at user scope.
