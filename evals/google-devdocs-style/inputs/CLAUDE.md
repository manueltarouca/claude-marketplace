# Betty

## Overview Of The Project

Betty is a narrative prototype. We are building it with Phaser 4 and TypeScript. The game is deployed to itch.io.

## Important Rules

- **ALWAYS** run the tests before committing. This is CRUCIAL.
- **NEVER** commit directly to main.
- Do not use `any` types. Ever.
- Don't forget that the asset pipeline is currently being rewritten, so it might be a bit unstable at this time.

## How Things Are Organized

The codebase is organized into a number of folders. Scenes live in `src/scenes`. Entities live in `src/entities`. The dialogue system, which is currently new, lives in `src/dialogue`.

## Running The Game

Simply run `npm run dev` and the game will be served on port 5173. If you want to run it on a different port, the `--port` flag can be utilized.

## Testing

Tests are run with Vitest. In order to run them, just execute `npm test`. Note that the snapshot tests will fail if you have not regenerated the atlas.

## Deployment

Deployment is done via the itch.io butler CLI. It will be run by the CI pipeline when a tag is pushed. For more info click here.
