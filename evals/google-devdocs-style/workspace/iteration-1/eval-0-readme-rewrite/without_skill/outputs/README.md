# Wasteland Kings

A top-down roguelike built with Phaser 4 and Vite.

## Getting started

You need Node 20 or newer.

```bash
npm install
npm run dev
```

Assets are not checked into the repository. The postinstall script downloads them
during `npm install`. To skip the download, set `SKIP_ASSETS`.

## Tests

Tests run under Vitest:

```bash
npm test
```

Coverage reports are written to `coverage/`.

Use `--filter` to run a subset. For example, to run only the physics tests:

```bash
npm test --filter physics
```

## Project structure

| Directory | Contents |
| --- | --- |
| `src/scenes/` | Scene definitions |
| `src/entities/` | Player, enemies, and other actors |
| `src/systems/` | Core game systems such as physics and spawning |

## Deploying

The CI pipeline deploys on every push to `main`. See the deployment setup docs for
details: <!-- TODO: link -->

## Contributing

Every pull request must pass the linter. Run it before you push:

```bash
npm run lint
```
