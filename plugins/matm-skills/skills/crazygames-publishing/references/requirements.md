# Technical, gameplay and quality requirements

Snapshot taken 2026-08-19 from `https://docs.crazygames.com/requirements/*`.
Re-read the live page before letting anyone architect around a figure.

## Size and files (`/requirements/technical/`)

| Limit | Figure |
| --- | --- |
| Total bundle | 250 MB |
| File count | 1500 |
| Initial download | ≤50 MB |
| Initial download, mobile homepage eligibility | ≤20 MB |
| Time to gameplay, externally hosted files | ≤20 s |

**How initial download is measured**: between the start of loading and the first
`Gameplay start` event, when the SDK is integrated. This is the whole reason
`gameplayStart()` is load-bearing — without it the measurement runs to the end
of the bundle. `/resources/getting-to-the-first-frame/` recommends loading only
what the first moments of play need, so the event can fire early.

## Browsers and devices

- Must work on **Chrome and Edge**. Safari is judged per game; games that behave
  badly there are disabled on Safari rather than rejected.
- Disabled on **Chromium OS** if they do not run smoothly on a **4 GB RAM**
  device.
- Must support **mouse, keyboard and touch** (touch when mobile is supported).
- Desktop should be playable in **landscape**; portrait is allowed and is fine
  for mobile-friendly games. Orientation is declared at submission.
- Mobile support is **optional** — "desktop and optionally mobile". Declaring it
  brings the ≤20 MB initial-download figure into play for homepage eligibility.
- Unity games are disabled on iOS by default because of memory crashes. Not
  relevant to a canvas game, but it signals how tight iOS memory is.

## Paths, sitelock, platform quirks

- **Relative paths only.** Absolute paths fail to load.
- **Sitelock** (`/resources/html5/sitelock/`) is described but the docs do not
  state whether it is mandatory. If implemented, whitelist `*.crazygames.com`,
  the locale domains (`crazygames.fr`, `.nl`, `.pl`, `.com.br`, `.jp`, `.co.kr`
  and others), `games.crazygames.com` (video ads), `https://app.crazygames.com`
  (Android) and `capacitor://app.crazygames.com` (iOS). Suggested check:
  hostname contains "crazygames" within the last three domain parts.
- **Mobile CSS**: disable text selection (`-webkit-user-select: none` and
  friends) so a long press does not select text or raise the iOS callout.
- **iOS audio**: iOS suspends the AudioContext on backgrounding. Call
  `audioContext.resume()` from inside a user gesture (a `touchend` handler)
  when `state === "suspended"`.

## Gameplay requirements (`/requirements/gameplay/`)

- **First-time experience**: "Games should land new users in gameplay
  immediately. If this is not feasible given the game specifics, a **maximum of
  1 click** is allowed." This is the only click budget given, and there is no
  stated seconds-to-gameplay limit for self-hosted games.
- **Legibility**: text and images must be readable at `devicePixelRatio: 1` at
  these sizes, which is what QA actually tests:
  - Desktop, not fullscreen: **907×510, 1216×684, 1077×606, 821×462**
  - Desktop, fullscreen: **1366×768, 1920×1080, 1536×864, 1280×720**
  - Mobile **800×450**, tablet **1080×607**
  The binding cases are 821×462 and 800×450 — design the HUD for those.
- **Frame-rate independence**: physics must behave consistently across **144 Hz
  and 165 Hz** monitors.
- **English is mandatory.** Use `systemInfo.locale` to select a language and
  fall back to English.
- Intuitive controls across device types; a restricted-keys guideline exists.
- **Custom in-game fullscreen buttons are prohibited** — the platform provides
  fullscreen and a custom one interferes with monetization.
- **No cross-promotion** of external or internal games. Exceptions: privacy and
  legal documents, community links that do not lead to a playable version,
  store links on desktop only, sequels in the same series, category backlinks.
- **PEGI 12** compliant; the audience is 13+. The docs give no further breakdown
  of violence, gore, gambling or language.

## Quality guidelines (`/requirements/quality/`)

Explicitly **advisory, not mandatory**, and containing no numbers at all. They
cover onboarding (in-gameplay, skippable, visual rather than textual,
core-loop-first), clarity of goals and controls, pacing, uniqueness, and
aesthetics — consistent resolution, no compression artifacts, consistent audio
levels, a coherent visual style, genre honesty, and UI whose "buttons are not
sized to encourage ads".

Treat these as design advice worth following, not as a checklist that gates
acceptance — describing them as requirements misleads the user about where the
real risk is.

## Not documented anywhere in the requirements pages

Worth stating explicitly, because each of these is commonly assumed:

- No framerate requirement of any kind
- No maximum load time in seconds for self-hosted bundles
- No required or banned file formats; no gzip/brotli mandate; no WebGL version
- No HTTPS or CORS clause
- No restriction on localStorage, cookies or IndexedDB
- No minimum or maximum canvas resolution, and no fixed aspect ratio
- No memory ceiling in MB
- No iframe or `window.top` rules
