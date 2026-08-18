# claude-marketplace

A Claude Code plugin marketplace named **`matm`**. It carries Manuel's own skills and
re-publishes third-party skill collections by pointing at their upstream repos.

## The one rule

**Never vendor third-party skills into this repo.** If an upstream repo publishes the
skills, add a git source that tracks it. Copies go stale silently and there is no signal
when they do. Only `plugins/matm-skills/` holds files we actually author.

## Layout

```
.claude-plugin/marketplace.json     the catalog — every plugin is one entry here
plugins/matm-skills/                the only plugin whose files live in this repo
  .claude-plugin/plugin.json
  skills/<name>/SKILL.md
```

## Adding a plugin

Pick the source by where the skills sit upstream:

| Upstream shape | Source |
|---|---|
| Skills at repo root (`music/SKILL.md`) | `{"source": "github", "repo": "owner/repo", "ref": "main"}` |
| Skills in a subdir (`skills/tweens/SKILL.md`) | `{"source": "git-subdir", "url": "https://github.com/owner/repo.git", "path": "skills", "ref": "master"}` |
| Repo unclonable, but published to npm | `{"source": "npm", "package": "name", "version": "^1.7.0"}` |
| Ours | `"source": "./plugins/matm-skills"` |

Use `git-subdir` whenever the skills are a subdirectory of a large repo — it sparse-clones
only that path. Phaser's repo is 470 MB; the sparse clone is 640 KB.

Reach for `npm` when a git source is impossible. `chrome-devtools` is the case: its repo
ships a perfectly good `.claude-plugin/marketplace.json`, but a `devtools-frontend`
submodule recursively drags in Chromium's `depot_tools` and LLVM, so `/plugin marketplace
add ChromeDevTools/chrome-devtools-mcp` times out cloning gigabytes. Its npm tarball is
2.3 MB with zero runtime dependencies. Prefer a version *range* over an exact pin — npm
sources derive no version of their own, so an exact pin means the plugin silently never
updates.

Upstream repos that ship no `.claude-plugin/plugin.json` need two extra fields on the
entry, or the skills won't be found:

```json
"skills": "./",
"strict": false
```

`"skills": "./"` because the skill directories sit at the plugin root with no `skills/`
wrapper. `"strict": false` because the marketplace entry is then the entire plugin
definition. Pin `ref` to the upstream default branch — it is `master` for Phaser and
`main` for ElevenLabs, so check rather than assume.

## Adding one of our own skills

Drop it at `plugins/matm-skills/skills/<name>/SKILL.md`. No marketplace edit needed — the
plugin already ships whatever is in that directory. Bundled scripts must be referenced as
`${CLAUDE_PLUGIN_ROOT}/skills/<name>/scripts/...`; a bare relative path breaks once the
plugin is installed from the cache. Bump `version` in `plugins/matm-skills/.claude-plugin/plugin.json`
so installed copies actually update.

Skill authoring itself (frontmatter, description triggers, evals) is the `skill-creator`
skill's job — use it rather than hand-writing SKILL.md.

## Before every push

```bash
claude plugin validate .
```

Check its **exit code**, not just its output — `claude plugin validate . | tail -2` in an
`&&` chain always reports success, because the pipe masks the failure. A broken
`marketplace.json` fails the whole marketplace for everyone who has it added, not just the
plugin you touched.

## An npm source needs its MCP config supplied here

npm tarballs usually exclude `.claude-plugin/`, so the entry has to carry what the
manifest would have. `chrome-devtools` declares its server inline:

```json
"mcpServers": {
  "chrome-devtools": {
    "command": "node",
    "args": ["${CLAUDE_PLUGIN_ROOT}/build/src/bin/chrome-devtools-mcp.js"]
  }
}
```

Run the binary out of `${CLAUDE_PLUGIN_ROOT}` rather than `npx package@version`. `npx`
would download a *second* copy on every launch and let the server drift out of sync with
the skills shipped beside it. `skills/` still gets scanned by default, so no `skills`
override is needed — only `"strict": false`, since there is no `plugin.json`.

`--autoConnect` attaches to Manuel's own running Chrome and its default profile instead of
launching an isolated one, so logged-in pages and the tabs he already has open are visible.
It needs Chrome 144+ and remote debugging enabled once at `chrome://inspect/#remote-debugging`;
Chrome must already be running when the server starts. Don't swap it for `--browserUrl` —
that needs Chrome relaunched with `--remote-debugging-port`, and since Chrome 136 that flag
is refused on the default profile, which forces a throwaway profile with no logins.

## elevenlabs runs from our fork

`elevenlabs` is sourced from `manueltarouca/elevenlabs-skills`, branch **`matm`**, not from
upstream. Upstream's `agents/` is a *skill* directory, but Claude Code also scans `agents/`
for subagents, so `agents/SKILL.md` was registered twice — once as the `agents` skill and
once as a subagent literally named `SKILL`. Nothing in a marketplace entry fixes it:
`"agents": []` validates but is ignored, and any path override fails validation with
`Invalid input` and drops the plugin to **0 skills**. The fork renames the directory to
`voice-agents/`; the skill's frontmatter `name:` is untouched, so the rename is invisible
to users.

Keep the fork honest:

```bash
cd ~/code/open-source/elevenlabs-skills
git fetch upstream
git checkout main && git merge --ff-only upstream/main && git push origin main
git checkout matm && git rebase main && git push --force-with-lease origin matm
claude plugin update elevenlabs@matm
```

`main` stays a pristine mirror so it always fast-forwards; `matm` is just main plus the one
rename. A conflict there means upstream touched `agents/` — re-do the rename rather than
resolving hunks. This is the only fork we maintain, and it exists solely because the fix is
unreachable from the marketplace entry. Don't fork to make cosmetic changes.

## Token cost is the real constraint

Every enabled plugin's skill descriptions load into *every* session. Run
`claude plugin details <plugin>` for the always-on number before recommending a scope:

- **User scope** (`~/.claude/settings.json`) — for plugins that are cheap or broadly useful.
  `matm-skills` (~277), `elevenlabs` (~1,331) and `chrome-devtools` (~630) live here.
- **Project scope** (`.claude/settings.json` in the repo) — for expensive or narrow plugins.
  `phaser` is ~3,221 always-on for 28 skills, so it is enabled only in `~/code/games/*`.

MCP tool schemas are *not* in the always-on number — they resolve at runtime when the
server starts, and for a server the size of chrome-devtools that is the larger cost.

## Renaming

The marketplace name `matm` is public: it is the `@matm` in every `plugin@matm` id and it
is written into `enabledPlugins` in user settings and in eight project settings files under
`~/code/games/`. Renaming means rewriting all of them. Don't do it casually.
