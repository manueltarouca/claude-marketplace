# Wasteland Kings

Wasteland Kings is a browser game built with [Phaser](https://phaser.io) 4, TypeScript, and
Vite. The repository holds the source and the build tooling; Vite serves the game in
development and bundles it to static files for release.

The source tree is a scaffold. Every file under `src/` is empty, so the project builds but
has no gameplay yet.

## Before you begin

You need:

- Node.js 20 or later, as declared in the `engines` field of `package.json`
- npm, or another package manager that runs npm lifecycle scripts

## Install

```bash
npm install
```

`npm install` runs the `postinstall` script, which calls `node scripts/fetch-assets.mjs` to
download game assets into `public/assets`.

Optional: to skip the download, set `SKIP_ASSETS=1`.

```bash
SKIP_ASSETS=1 npm install
```

The repository doesn't contain `scripts/fetch-assets.mjs`. Until you add that file,
`postinstall` fails and takes the whole install with it, because Node can't resolve the
missing module before it reads `SKIP_ASSETS`. To install the dependencies anyway, skip the
lifecycle scripts:

```bash
npm install --ignore-scripts
```

## Run the game locally

```bash
npm run dev
```

Vite starts a development server on port `5173` and reloads the page when you edit a file
under `src/`. Both `package.json` and `vite.config.ts` set the port, so change it in both
places if you move it.

## Build for production

```bash
npm run build
```

The build runs `tsc` first and stops if type checking reports an error. Vite then bundles
the game to `dist/`, targeting `es2022`.

To serve the contents of `dist/` and check the bundle before you deploy it, run:

```bash
npm run preview
```

## Test

```bash
npm test
```

The command runs Vitest once, without watch mode, and reports coverage.

## Lint

```bash
npm run lint
```

ESLint checks the `src` directory.

## Project layout

```
src/
  scenes/     Phaser scenes: BootScene, MenuScene, GameScene
  systems/    game systems: Spawner, Loot, Physics
  entities/   game objects: Player, Raider, Turret
public/       static files, including the assets that postinstall downloads
vite.config.ts
package.json
```

## Dependencies

| Package | Version range | Role |
|---|---|---|
| `phaser` | `^4.0.0` | game framework, the only runtime dependency |
| `vite` | `^6.0.0` | development server and bundler |
| `vitest` | `^2.1.0` | test runner |
| `typescript` | `^5.6.0` | type checking during the build |
| `eslint` | `^9.0.0` | linting |

## License

`package.json` marks the package as private and declares no license, so the code carries no
grant of rights. Add a `license` field before you publish or distribute the game.
