# Betty

## Overview

Betty is a narrative prototype built with Phaser 4 and TypeScript. It deploys to itch.io.

## Rules

- Run the tests before you commit. This is required, not advisory.
- Never commit directly to `main`.
- Never use `any` types. There is no exception.
- Expect the asset pipeline to be unstable. It is being rewritten.

## Layout

- `src/scenes` — scenes.
- `src/entities` — entities.
- `src/dialogue` — the dialogue system.

## Run the game

To start the dev server, run `npm run dev`. The game is served on port 5173.

Optional: to serve on a different port, pass the `--port` flag.

## Test

Betty uses Vitest. To run the tests, run `npm test`.

The snapshot tests fail if you haven't regenerated the atlas, so regenerate it first.

## Deploy

The CI pipeline deploys through the itch.io butler CLI when you push a tag. For more
information, see the butler documentation.
