# Wasteland Kings

Wasteland Kings is a top-down roguelike built with Phaser 4 and Vite.

## Get started

You need Node 20 or later.

1. Install the dependencies:

   ```
   npm install
   ```

2. Start the dev server:

   ```
   npm run dev
   ```

The repository doesn't include the assets. The postinstall script downloads them for you. To
skip the download, set the `SKIP_ASSETS` environment variable.

## Run the tests

Wasteland Kings uses Vitest. To run the full suite, run `npm test`. Vitest writes coverage
reports to `coverage/`.

To run only the physics tests, pass the `--filter` flag:

```
npm test --filter physics
```

## Project structure

The source code is organized into these directories:

- `src/scenes/` — Scene definitions.
- `src/entities/` — The player, the enemies, and the other actors.
- `src/systems/` — Core game systems such as physics and spawning.

## Deploy

The CI pipeline handles deployment. Pushing to `main` triggers it. For more about the
deployment setup, see [Deployment setup](DEPLOYMENT_SETUP_URL).

## Contribute

Contributions are welcome. Every pull request must pass the linter, so run `npm run lint`
before you push.
