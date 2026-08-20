# Wasteland Kings

A browser game built with [Phaser](https://phaser.io) 4, TypeScript, and Vite.

Version 0.4.2. The package is marked `private`, so it is not published to npm.

> **Status: early scaffold.** The directory layout and build tooling are in place, but
> every file under `src/` is currently empty, and several files the configuration refers
> to are not in the repository yet. See [Current state](#current-state) before you try to
> run anything.

## Requirements

- Node.js 20 or newer (declared in `engines`)

## Getting started

```bash
npm install
npm run dev
```

The dev server listens on port 5173, set both in the `dev` script and in
`vite.config.ts`.

`npm install` runs a `postinstall` hook that executes `scripts/fetch-assets.mjs`, which
downloads game assets into `public/assets`. That script is not present in this repository
yet, so install will fail until it is added — see [Current state](#current-state).

## Scripts

| Command | What it does |
| --- | --- |
| `npm run dev` | Starts the Vite dev server on port 5173. |
| `npm run build` | Type-checks with `tsc`, then builds with Vite into `dist/`. |
| `npm run preview` | Serves the built `dist/` output locally. |
| `npm test` | Runs the Vitest suite once, with coverage. |
| `npm run lint` | Runs ESLint over `src`. |

## Configuration

Build and server options live in `vite.config.ts`:

| Option | Value |
| --- | --- |
| `server.port` | `5173` |
| `build.target` | `es2022` |
| `build.outDir` | `dist` |

### Environment variables

| Variable | Effect |
| --- | --- |
| `SKIP_ASSETS=1` | Skips the asset download performed by the `postinstall` script. |

## Project structure

```
.
├── package.json
├── vite.config.ts
└── src
    ├── scenes      Phaser scenes: BootScene, MenuScene, GameScene
    ├── systems     Gameplay systems: Physics, Spawner, Loot
    └── entities    Game objects: Player, Raider, Turret
```

The three groupings follow the usual Phaser split: scenes drive the game loop and own the
lifecycle, entities are the objects placed in a scene, and systems hold behaviour that cuts
across entities.

## Dependencies

**Runtime**

- `phaser` ^4.0.0

**Development**

- `vite` ^6.0.0
- `vitest` ^2.1.0
- `typescript` ^5.6.0
- `eslint` ^9.0.0

## Current state

These are gaps between what the configuration expects and what the repository contains.
They are listed so nobody loses time rediscovering them.

- **All source files are empty.** Every `.ts` file under `src/` is 0 bytes. The tree
  describes the intended architecture; none of it is implemented.
- **`scripts/fetch-assets.mjs` is missing.** The `postinstall` hook calls it, so a plain
  `npm install` will fail. There is no `public/` directory either.
- **No `index.html`.** Vite needs an entry HTML file at the project root for `dev`,
  `build`, and `preview` to work.
- **No `tsconfig.json`.** The `build` script invokes `tsc`, which needs one.
- **No ESLint configuration.** `npm run lint` needs a config file for ESLint 9 (flat
  config, `eslint.config.js`).
- **No coverage provider installed.** `npm test` passes `--coverage`, which Vitest
  implements through a separate provider package that is not in `devDependencies`.

## License

No license is declared. `package.json` sets `"private": true` and includes no `license`
field.
