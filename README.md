# matm — a personal Claude Code marketplace

My own skills, plus third-party skill collections tracked **live from their upstream
repos** rather than copied in. Upstream stays the source of truth; `claude plugin
update <plugin>@matm` pulls new commits.

## Install

```bash
claude plugin marketplace add manueltarouca/claude-marketplace
claude plugin install matm-skills@matm     -s user -y
claude plugin install elevenlabs@matm      -s user -y
claude plugin install chrome-devtools@matm -s user -y
claude plugin install phaser@matm          -s project -y   # run inside a game project
```

## Plugins

| Plugin | Source | Ships | Notes |
|---|---|---|---|
| `matm-skills` | this repo, `plugins/matm-skills` | 1 skill | `codex-imagegen` — image generation via the local Codex CLI, no API keys |
| `phaser` | `phaserjs/phaser` → `skills/` (sparse) | 28 skills | Phaser 4. ~3.2k always-on tokens, so enable per-project |
| `elevenlabs` | our fork of `elevenlabs/skills` | 10 skills | TTS, music, SFX, dubbing, STT, voice changer/isolator. Needs `ELEVENLABS_API_KEY` |
| `chrome-devtools` | npm `chrome-devtools-mcp` | 6 skills + MCP server | Browser automation, performance traces, LCP and memory-leak analysis, a11y audits |

## Why these sources

Upstream repos are the source of truth; this repo mostly holds pointers. Getting the
pointer right is the whole job:

- **`git-subdir`** — Phaser's repo is ~470 MB but its skills are one `skills/`
  subdirectory. Sparse-cloning just that path costs 640 KB.
- **npm** — `chrome-devtools-mcp`'s repo publishes its own marketplace, but a
  `devtools-frontend` submodule recursively pulls Chromium's `depot_tools` and LLVM, so
  cloning it times out. Its npm tarball is 2.3 MB with zero dependencies. The MCP server
  runs from `${CLAUDE_PLUGIN_ROOT}`, so it can't drift from the skills beside it.
- **A fork** — only for `elevenlabs`, and only because the fix is unreachable from a
  marketplace entry: upstream's `agents/` skill directory also gets scanned as a subagent
  directory. Our `matm` branch renames it to `voice-agents/`; `main` stays a clean mirror.

Neither Phaser nor ElevenLabs ships a `.claude-plugin/plugin.json`, so those entries set
`"skills": "./"` and `"strict": false` — the marketplace entry is the whole plugin
definition.

## Adding a plugin

See `CLAUDE.md` for the full decision table. Short version:

- **Skills at the repo root** — `{"source": "github", "repo": "owner/repo"}` plus
  `"skills": "./"` and `"strict": false`.
- **Skills in a subdirectory** — `{"source": "git-subdir", "url": "...", "path": "skills"}`,
  same two fields.
- **Repo too heavy to clone** — `{"source": "npm", "package": "...", "version": "^1.0.0"}`,
  and declare any `mcpServers` inline on the entry.
- **My own** — add `plugins/matm-skills/skills/<name>/SKILL.md`; it ships with the plugin
  already listed. Reference bundled files with `${CLAUDE_PLUGIN_ROOT}`.

Then `claude plugin validate .` — check the exit code, not just the output — before pushing.

## Token cost

`claude plugin details <plugin>` reports the always-on cost a plugin adds to every
session. Check it before enabling anything at user scope.
