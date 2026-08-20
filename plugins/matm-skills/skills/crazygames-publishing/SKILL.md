---
name: crazygames-publishing
description: Research, build and ship HTML5 games to CrazyGames — the documented technical limits (bundle size, load budget, legibility resolutions), the v3 JS SDK (init, loading and gameplay events, ads, banners, data, user), the advertisement rules that cause silent rejection, and the Basic vs Full Launch process. Crucially it separates what the docs actually say from the folklore that circulates about web game portals. Use this whenever the user mentions CrazyGames, publishing or submitting a browser game, web game portals, ad-share or ad-revenue platforms for games, rewarded or interstitial ads in a game, game covers or store art, "will my game get accepted", HTML5 game monetization, or is designing a browser game they intend to distribute — even if they never say "CrazyGames" by name. Also use it when reviewing an existing web game for portal readiness.
---

# Shipping to CrazyGames

CrazyGames publishes browser games and shares ad revenue. Its requirements are
unusually specific — real numbers for bundle size, real pixel dimensions QA
tests legibility at — and those numbers constrain design decisions you make on
day one, not at submission. A game built at the wrong internal resolution or
with a menu in front of gameplay is expensive to fix later.

## The rule that matters most: documented, or folklore?

Web game portals attract an enormous amount of confident, uncited advice. Much
of it is wrong for CrazyGames specifically.

**Every constraint you state should be traceable to a docs page, and anything
you cannot trace should be labelled as not documented.** This is not pedantry.
A team that believes in an undocumented 60 FPS requirement will spend a week
optimising something nobody checks, while missing the 1-click-to-gameplay rule
that is real and will get them rejected.

Things people routinely "know" that the docs **do not say** (verified against
the live docs):

- No 60 FPS or any framerate requirement
- No maximum load time in seconds for self-hosted bundles (there *is* a ≤20 s
  figure, but only for externally hosted files)
- No required or banned image/audio formats, no gzip/brotli mandate
- No HTTPS or CORS clause
- No ban on `localStorage` (the Data module is *recommended*, not mandatory)
- No minimum canvas resolution or fixed aspect ratio
- No stated penalty for skipping the SDK gameplay events
- No published revenue split and no review turnaround SLA

When you are unsure, say "the docs do not specify this" rather than filling the
gap from general knowledge of Poki, Itch or Newgrounds. Being explicit about the
boundary is more useful than a confident guess, because it tells the user which
decisions are constrained and which are theirs.

## Verify before you advise

The bundled references are a snapshot and the docs change. For anything
load-bearing — a size limit someone is about to architect around, an SDK call
someone is about to ship — re-read the live page and note the date.

Start at `https://docs.crazygames.com/` but **follow the links**; the index page
carries no detail. The pages that matter:

| Page | Path |
| --- | --- |
| Technical limits | `/requirements/technical/` |
| Gameplay + first-time experience | `/requirements/gameplay/` |
| Advertisement rules | `/requirements/ads/` |
| Quality guidelines (advisory) | `/requirements/quality/` |
| Cover art specs | `/requirements/game-covers/` |
| SDK overview and modules | `/sdk/intro/`, `/sdk/game/`, `/sdk/video-ads/`, `/sdk/banners/`, `/sdk/data/`, `/sdk/user/` |
| Getting to the first frame | `/resources/getting-to-the-first-frame/` |
| Basic Launch metrics | `/resources/basic-launch-metrics/` |

**The SDK is v3.** The v2 documentation is still live at `/sdk/html5-v2/*` and
sample code found online is frequently v2. v3 requires an awaited `init()` and
renamed the loading calls. If you see `sdkGameLoadingStart()`, you are reading
v2.

## The numbers that shape the design

These are the documented figures that change what you build, rather than what
you check at the end.

| Constraint | Figure | What it forces |
| --- | --- | --- |
| Clicks to gameplay | **max 1** | No menu, no title screen, no loadout before play |
| Initial download | **≤50 MB**, **≤20 MB** for mobile homepage eligibility | Procedural art, or aggressive lazy-loading |
| Total bundle / file count | **250 MB** / **1500 files** | Rarely binding for a 2D game |
| Legibility tested at | desktop **821×462** (smallest), mobile **800×450** | Internal resolution and font size; fine detail dies here |
| Frame-rate independence | identical physics at **144 Hz and 165 Hz** | Fixed-step accumulator, never one step per rAF |
| Input | mouse **and** keyboard **and** touch | A one-verb, pointer-driven design satisfies all three cheaply |
| Midgame ad frequency | **1 per 3 minutes**, enforced server-side | Design the loop so natural breaks are ≥3 min apart |
| Custom fullscreen button | **prohibited** | The platform provides it; a custom one interferes with monetization |
| English | **mandatory** | Use `systemInfo.locale` to pick a language, fall back to English |
| Paths | **relative only** | Absolute paths fail to load in the portal iframe |

Read `references/requirements.md` for the complete set including browser and
device support, sitelock domains, and the iOS audio-context caveat.

## The SDK, minimally

For a plain HTML5/Canvas game, four calls carry almost all the value:

```html
<script src="https://sdk.crazygames.com/crazygames-sdk-v3.js"></script>
```

```js
await window.CrazyGames.SDK.init();          // v3 requires this; await it on the loading screen

window.CrazyGames.SDK.game.loadingStart();   // beginning to load assets
window.CrazyGames.SDK.game.loadingStop();    // assets ready
window.CrazyGames.SDK.game.gameplayStart();  // real gameplay begins or resumes
window.CrazyGames.SDK.game.gameplayStop();   // every break: pause, menu, level end, before an ad
```

`gameplayStart` is worth getting right for a mechanical reason rather than a
policy one: **initial download is measured from the start of loading to the
first `gameplayStart` event.** Omit the call and your measured initial download
becomes the entire bundle, which is how a small game fails a 50 MB check.

Do not fire these on focus change or when the player leaves the game area —
the platform handles that, and doing it yourself double-counts.

`references/sdk.md` has the full module surface (data, user, banners,
leaderboards, multiplayer), the local-testing switches, and the v2→v3 deltas.

## Ads: the part that causes silent rejection

The ads page states that games are **rejected without feedback** when the
advertisement requirements are not followed, so this is the section to be
careful about.

Two video types exist — `"midgame"` and `"rewarded"`. There is no separate
"interstitial" or "preroll" type in the API.

The non-negotiables:

- **Mute in-game audio** when the ad starts, unmute only when it finishes
- **Pause the game** — block input or show a spinner
- **Never during active gameplay.** Only at transitions: death, level end, map
  change. An ad must not come as a surprise
- **Never on a navigation button** (menu, settings, shop)
- On `adError`, carry on normally and **do not grant the reward**
- The game must remain fully playable with an adblocker active

Rewarded ads have their own rules — the reward must be optional, a non-ad
alternative must exist, and skip/continue buttons must be visually identical.
`references/ads.md` covers those, the banner size table and placement rules,
and every error code.

For a death-loop arcade game the natural design is: `gameplayStop()` on death →
offer a rewarded revive → `gameplayStart()` on continue. That satisfies the
"only at transitions" rule by construction.

## Checking a build

Run the bundled checker against a built game to catch the mechanically
verifiable failures before submission:

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/crazygames-publishing/scripts/check-build.mjs" <dist-dir>
```

It measures total size and file count against the documented limits, estimates
the initial download, and flags absolute paths, a missing or v2 SDK, missing
gameplay events, and custom fullscreen calls. It reports what it cannot check —
legibility, ad placement and originality are human judgements — rather than
implying a pass.

## Launch is two stages

**Basic Launch**: the game goes live with no customization. The SDK is
*optional* and monetization is disabled — ads are ignored even if integrated.
This is a real audience test, not a staging environment.

**Full Launch**: SDK required, monetization and platform features unlocked.

Basic Launch ends once the game has been live **≥7 days** and reached **≥500
plays**, extending to a maximum of **21 days** if it does not. The published
figures for play time, D1 retention and conversion are **observed benchmarks
from successful titles, not pass thresholds** — no numeric bar is published, so
present them as context rather than as a target to clear.

`references/launch.md` covers the metrics, the listed rejection reasons and the
cover-art specifications required at submission.

## Reference files

Read these when you reach the relevant stage rather than all at once.

| File | Read it when |
| --- | --- |
| `references/requirements.md` | Deciding resolution, bundle strategy, device support, or auditing a game against the technical and gameplay rules |
| `references/sdk.md` | Integrating or debugging the SDK, or porting v2 sample code |
| `references/ads.md` | Placing any ad or banner, or reviewing ad placement before submission |
| `references/launch.md` | Preparing a submission, producing cover art, or interpreting Basic Launch numbers |
