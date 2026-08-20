# Betty

Betty is a narrative prototype built with Phaser 4 and TypeScript.

## Run the game

To start the dev server, run `npm run dev`. The game is served on port 5173.

Optional: to use a different port, pass `--port`.

## Run the tests

Betty uses Vitest. To run the suite, run `npm test`.

If you have not regenerated the atlas, the snapshot tests fail. Run `npm run atlas` first.

## Deploy the game

Betty deploys to itch.io with the butler CLI.

CI runs the deployment when you push a tag. Set a `BUTLER_API_KEY` secret in the repository first, or the deployment fails.

To deploy by hand instead, build the game, then run:

```
butler push dist matm/betty:web
```

## Layout

- `src/scenes` holds scene definitions.
- `src/entities` holds the player and NPCs.
- `src/dialogue` holds the dialogue system.
