// Error and log messages for the asset pipeline CLI.

export const ERRORS = {
  missingConfig:
    "Can't find assets.yaml in the current directory. Create one, or pass --config with a path to it.",

  badYaml:
    "Can't parse assets.yaml: line 12 expects a string, found a list. Quote the value or remove the list.",

  noAssetDir:
    "No asset directory given. Pass --assets with the path to your sprite source directory.",

  authExpired:
    "Your upload credentials expired. Run `assets login` to sign in again.",

  writeFailed:
    "Can't write to the output directory. Check that it exists and that you have write permission.",

  spriteMissing: (name: string) =>
    `Sprite ${name} is listed in assets.yaml but not on disk. Add the file, or remove the entry from the config.`,

  quotaHit:
    "Upload quota reached for this account. Wait for the quota to reset, or upgrade the plan.",
};

export const LOGS = {
  startup: "Starting the asset pipeline.",
  packing: "Packing the atlas.",
  done: "Finished packing the atlas.",
  retry: "Retrying the upload.",
};
