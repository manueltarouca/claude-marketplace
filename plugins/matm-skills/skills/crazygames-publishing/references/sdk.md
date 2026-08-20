# The CrazyGames JS SDK (v3)

Snapshot taken 2026-08-19 from `https://docs.crazygames.com/sdk/*`.

**The current SDK is v3.** The v2 docs are still live at `/sdk/html5-v2/*` and
most sample code found by search is v2. Tell them apart by the loading calls:
`sdkGameLoadingStart()` is v2, `loadingStart()` is v3.

```html
<script src="https://sdk.crazygames.com/crazygames-sdk-v3.js"></script>
```

There is no documented npm package.

## Initialisation

```js
await window.CrazyGames.SDK.init();
```

v3 **requires** this and the SDK is unusable until it resolves. Await it on the
loading screen, before the game starts.

```js
window.CrazyGames.SDK.environment   // "local" | "crazygames" | "disabled"
```

A plain property in v3 — in v2 it was an async getter. The same is true of
`isUserAccountAvailable` and `systemInfo`. v3 errors are objects with `code` and
`message` rather than strings.

Modules: `ad`, `banner`, `game`, `user`, `data`, plus in-game purchases and
leaderboards.

## The `game` module

```js
SDK.game.loadingStart();
SDK.game.loadingStop();
SDK.game.gameplayStart();
SDK.game.gameplayStop();
```

- `loadingStart` / `loadingStop` track how long loading takes. Supported for
  HTML5, Construct and GameMaker; **not** supported in Unity or Godot.
- `gameplayStart` / `gameplayStop` tell the platform when someone is actually
  playing, so it can avoid resource-intensive work during play. Call
  `gameplayStop` at *every* break: pause, menu, level end, and before any ad.
- **Do not** call these on focus change or when the player leaves the game area.
  The platform handles that.

**Consequence of omitting them**: the docs state no penalty. The only documented
mechanical effect is that initial-download size is measured up to the first
`Gameplay start`, so omitting it inflates your measured size against the 50 MB
and 20 MB thresholds. Claims that omission causes rejection are not in the docs.

Other methods: `happytime()` (a celebration cue — the docs say "use this feature
sparingly"), `reportGameCompletedPercentage(value)`, `setGameContext(obj)` /
`clearGameContext()`, `addSettingsChangeListener` / `removeSettingsChangeListener`,
`settings`, and the multiplayer surface (`updateRoom`, `leftRoom`,
`addJoinRoomListener`, `inviteLink(obj)`, `getInviteParam(str)`, `inviteParams`,
`isInstantMultiplayer`). `showInviteButton` / `hideInviteButton` are
**deprecated** in favour of Room Data.

There is no `requestFullscreen`, `isFullscreen` or `getSystemInfo` on the game
module — system info lives on `user`.

## The `data` module — the answer to "can I use localStorage?"

```js
SDK.data.getItem(key);      // string | null
SDK.data.setItem(key, value);
SDK.data.removeItem(key);
SDK.data.clear();
```

localStorage is **not documented as blocked**, and the SDK itself falls back to
LocalStorage for logged-out users then migrates on login. The docs recommend
relying on the Data module rather than local saves because it syncs across
devices.

Limit **1 MB per user**; exceeding it throws `dataLimitExcedeed` (spelled that
way in the docs). Saves are debounced around 1 s, occasionally up to 30 s.

## The `user` module

- `isUserAccountAvailable` — property; false on external embedding domains
- `getUser()` → `{ __dangerousUserId, username, profilePictureUrl }` or null
- `systemInfo` → `{ countryCode, locale, device.type, os, browser, applicationType }`
- `getUserToken()` → JWT with a **1 hour** lifetime; verify server-side
- `showAuthPrompt()`, `showAccountLinkPrompt()`
- `addAuthListener` / `removeAuthListener` — login fires; logout does not, the
  page refreshes instead
- `listFriends({ page, size })` — page starts at 1, **max size 50**

## Local testing

- `localhost` / `127.0.0.1` serve demo ads and log to the console
- `?useLocalSdk=true` forces local behaviour on any domain
- `crazygames.com/preview` is the realistic simulator

## v2 → v3 migration

| v2 | v3 |
| --- | --- |
| `sdkGameLoadingStart()` | `loadingStart()` |
| `sdkGameLoadingStop()` | `loadingStop()` |
| async getters | plain properties (`environment`, `isUserAccountAvailable`, `systemInfo`) |
| string errors | `{ code, message }` objects |
| — | `await init()` now required |
