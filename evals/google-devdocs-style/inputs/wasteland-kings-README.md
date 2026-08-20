# Wasteland Kings

## What Is This Project?

Wasteland Kings is a top-down roguelike built with Phaser 4 and Vite. We wanted to make a game that showcases what modern web tech can do, and this is a testament to that vision.

## Getting Started

First, you will need Node 20 or above installed. Then simply run `npm install` — it should only take a minute or two. Once that is done, the dev server can be started by running `npm run dev`.

Note that the assets are not included in the repository. They will be downloaded automatically by the postinstall script. If you want to skip this, the `SKIP_ASSETS` env var can be set.

## Running The Tests

We use Vitest. Just run `npm test`. Coverage reports will be generated into `coverage/`.

In order to run only the physics tests, you can utilize the `--filter` flag, e.g. `npm test --filter physics`.

## Project Structure

The source code is organized into a number of directories:

- **src/scenes/** — Scene definitions
- **src/entities/** — Player, enemies, etc.
- **src/systems/** — Core game systems (physics, spawning, etc.)

## Deploying

Deployment is handled by the CI pipeline. It will be triggered when you push to main. For more information about our deployment setup, click here.

## Contributing

We welcome contributions! Please note that all PRs must pass the linter. Simply run `npm run lint` before pushing and you should be fine.
