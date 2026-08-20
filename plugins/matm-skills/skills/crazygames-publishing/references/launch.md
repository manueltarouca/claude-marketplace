# Launch, submission and store assets

Snapshot taken 2026-08-19 from `/resources/basic-launch-metrics/`,
`/requirements/game-covers/` and `/faq/`.

## Two stages

**Basic Launch** — the game goes live with no customization. The SDK is
optional, monetization is off, and ads are ignored even if integrated. This is a
live audience test rather than a staging environment.

**Full Launch** — SDK required; monetization and platform features unlocked.

## Leaving Basic Launch

The period ends once the game has been live **≥7 days** *and* reached **≥500
plays**. If 500 plays are not reached it extends to a maximum of **21 days**.

Three KPIs are published:

| KPI | Published figure |
| --- | --- |
| Average play time | "successful titles often see 10+ minutes" |
| D1 retention | "strong games often achieve 10–15%" |
| Conversion | "top-performing titles typically convert 80%+" |

These are stated as **observed benchmarks from successful titles, not pass
thresholds**. No numeric bar is published. Presenting them as targets to clear
overstates what the docs say — use them as orientation.

## Rejection reasons (from the FAQ)

- Bugs or broken mechanics
- Missing English support
- Unoriginal content — clones, asset flips
- Inappropriate themes
- Failing the developer requirements or PEGI 12

Plus, from the ads page: advertisement requirements not followed, **rejected
without feedback**.

No formal QA checklist is published. Reviewers are described as evaluating
quality and legibility (at the pixel sizes in `requirements.md`), performance,
originality, and time-to-gameplay for externally hosted assets.

## Store assets required at submission

Three covers, no borders, no store logos, nothing blurry:

| Cover | Aspect | Size |
| --- | --- | --- |
| Landscape | 16:9 | 1920×1080 |
| Portrait | 2:3 | 800×1200 |
| Square | 1:1 | 800×800 |

Optional video: **15–20 s** (longer is cut to 20 s), **≤50 MB**, 1080p in both
landscape 16:9 and portrait 2:3. No audio needed. The static cover must be the
opening frame. No black screens, cursors or promotional text.

## Other

- Developer support becomes available at **50,000 combined plays**
- Updates typically go live within the same working day

## Not documented

- **Review turnaround time** for a new submission
- **Revenue share percentage**
- **Submission packaging** — zip layout, whether `index.html` must be at the
  root
