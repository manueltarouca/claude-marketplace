# Advertisement rules and the ad/banner API

Snapshot taken 2026-08-19 from `/requirements/ads/`, `/sdk/video-ads/`,
`/sdk/banners/` and `/resources/midgame-ads-pacing/`.

The ads page states that games are **rejected without feedback** when these
requirements are not followed. Of everything in the docs, this is the section
where a mistake is most expensive and least diagnosable.

## Video ads

Two types, and the strings are exactly these:

```js
window.CrazyGames.SDK.ad.requestAd("midgame", {
  adStarted:  () => {},          // no args — mute audio and pause here
  adFinished: () => {},          // no args — unmute, resume, grant any reward here
  adError:    (error) => {},     // error = { code, message }
});

window.CrazyGames.SDK.ad.hasAdblock();   // boolean
```

There is **no** separate "interstitial" or "preroll" type. HTML5 uses callbacks;
promise forms exist for Construct and Godot.

Error codes: `adsDisabledBasicLaunch`, `unfilled`, `adblock`, `adCooldown`,
`other`.

### Frequency

Midgame ads are **automatically capped at one per 3 minutes**, enforced
server-side, returning `adCooldown` if you ask sooner. There are extra
safeguards around game start and around rewarded ads. Because the cap is
enforced for you, the docs tell you to request freely at natural breaks rather
than building your own timer — a home-grown timer can only be more conservative
than the platform's, never less.

There is **no documented minimum interval for rewarded ads**, only guidance to
limit frequency and use cooldowns.

### Mandatory behaviours

- **Mute in-game audio** on `adStarted`; unmute only on completion. Explicit.
- **Pause the game** — disable buttons or show a blocking spinner.
- **Never interrupt active gameplay.** Only at transitions: level change, map
  transition, death. "Advertisements should not be shown while a user is
  playing" and "should not come as a surprise."
- **Never attach a midgame ad to a navigation button** (main menu, settings,
  shop).
- No ads before the player has had a reasonable amount of gameplay; midgame ads
  are discouraged before the tutorial or the first 3–5 minutes.
- On `adError`, **continue gameplay normally** and **do not grant the reward**.

### Rewarded ads

- The reward must be optional and clearly signposted with a video icon
- A non-ad alternative must exist
- A level must never be completable *only* via a rewarded ad
- Never chain multiple ads for one reward
- The request button must not sit on an active gameplay screen
- Skip and continue buttons must be identical in size, font and colour
- Celebrate on `adFinished`
- Out-of-lives ads must not appear on every death

## Banners

```js
SDK.banner.requestBanner({ id, width, height });
SDK.banner.requestResponsiveBanner(containerId);
SDK.banner.clearBanner(containerId);
SDK.banner.clearAllBanners();
```

Static sizes: **728×90, 300×250, 320×50, 468×60, 320×100**.
Responsive picks from: 970×90, 970×250, 728×90, 468×60, 336×280, 320×50,
300×600, 300×250, 250×250, 160×600, 120×600.

Rules:

- Only on screens open **≥5 seconds on average**
- **Never during gameplay**
- Must not block UI at any size
- **Max 2 per screen**
- Fully inside the game window, container fully visible, CSS dimensions matching
  the banner
- **≥30 s between refreshes** on the same container
- **Max 120 refreshes per session** per banner size
- Blocked while a video ad plays

Errors: `bannersDisabledBasicLaunch`, `unfilled`, `missingId`, `notVisible`,
`noAvailableSizes`, `notCreated`, `videoAdPlaying`, `invalidSize`,
`bannerCooldown`, `maxRefreshReached`, `bannersDisabledMobileApp`, `other`.

## Adblock

The game must **fully function** with an adblocker active. You may gate *extra*
content — skins, bonus levels — and show a notice, but you must not block or
penalise the player, must not use popups, and must not leave a rewarded button
clickable with no effect.

## Basic Launch

Ads are disabled entirely and will be ignored even if integrated. Only ads
served through the SDK are permitted; external monetization is prohibited.

## Designing the loop around this

The rules reduce to one shape: **ads live at loop boundaries, never inside the
loop.** A game with frequent, cheap deaths gets this for free — death is a
transition, the player expects a pause there, and a rewarded revive is the
canonical use of the format. A game with 20-minute sessions and no natural break
has to invent one, and inventing a break purely to host an ad is exactly what
"should not come as a surprise" is aimed at.
