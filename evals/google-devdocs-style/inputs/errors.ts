// Error and log messages for the asset pipeline CLI.

export const ERRORS = {
  missingConfig: "Error!",

  badYaml: "Invalid configuration!",

  noAssetDir: "You failed to provide an asset directory.",

  atlasTooBig: "Oops! Something went wrong while packing the atlas.",

  badChannel: "Unexpected token",

  authExpired:
    "Sorry, we could not authenticate you. Please try again later or contact support.",

  writeFailed: "Could not not write the output file.",

  spriteMissing: (name: string) => `Sprite ${name} is bad`,

  quotaHit: "You have used too much quota. Aborting.",

  sanityCheckFailed: "Sanity check failed - the atlas is insane.",
};

export const LOGS = {
  startup: "Starting up...",
  packing: "The atlas will be packed now.",
  done: "All done!",
  retry: "Retrying...",
};
