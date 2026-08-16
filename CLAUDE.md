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
| Ours | `"source": "./plugins/matm-skills"` |

Use `git-subdir` whenever the skills are a subdirectory of a large repo — it sparse-clones
only that path. Phaser's repo is 470 MB; the sparse clone is 640 KB.

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

It catches malformed entries and missing fields. A broken `marketplace.json` fails the
whole marketplace for anyone who has it added, not just the plugin you touched.

## Token cost is the real constraint

Every enabled plugin's skill descriptions load into *every* session. Run
`claude plugin details <plugin>` for the always-on number before recommending a scope:

- **User scope** (`~/.claude/settings.json`) — for plugins that are cheap or broadly useful.
  `matm-skills` (~260 tok) and `elevenlabs` (~1k tok) live here.
- **Project scope** (`.claude/settings.json` in the repo) — for expensive or narrow plugins.
  `phaser` is ~3.2k always-on for 28 skills, so it is enabled only in `~/code/games/*`.

## Renaming

The marketplace name `matm` is public: it is the `@matm` in every `plugin@matm` id and it
is written into `enabledPlugins` in user settings and in eight project settings files under
`~/code/games/`. Renaming means rewriting all of them. Don't do it casually.
