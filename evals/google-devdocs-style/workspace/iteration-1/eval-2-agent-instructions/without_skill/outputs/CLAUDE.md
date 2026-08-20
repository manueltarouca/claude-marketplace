# Betty

Betty is a narrative prototype built with Phaser 4 and TypeScript, and deployed to
itch.io.

## Rules

- Run the tests before every commit.
- Never commit directly to `main`.
- Never use `any` types.

## Layout

```
src/scenes/      scenes
src/entities/    entities
src/dialogue/    dialogue system (new)
```

## Running the game

```bash
npm run dev
```

The game is served on port 5173. Pass `--port` to serve it on a different port.

## Testing

Tests run under Vitest:

```bash
npm test
```

Snapshot tests fail unless the atlas has been regenerated, so regenerate it first.

## Deployment

CI deploys with the itch.io `butler` CLI when a tag is pushed.

## Known instability

The asset pipeline is being rewritten and is unstable right now.
