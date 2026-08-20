// Error and log messages for the asset pipeline CLI.

export const ERRORS = {
  missingConfig:
    "No config file found. Create an assets.yaml in the project root, or pass --config <path>.",

  badYaml:
    "The config file isn't valid YAML. Check the reported line and column, then run the command again.",

  noAssetDir:
    "No asset directory specified. Pass the directory to pack, for example: assets pack ./src/assets.",

  atlasTooBig:
    "The packed atlas exceeds the maximum texture size. Reduce the sprite count, lower the padding, or raise maxSize in the config.",

  badChannel:
    "Unrecognized release channel. Use one of: stable, beta, or nightly.",

  authExpired:
    "Your credentials have expired. Run `assets login` to sign in again, then retry the upload.",

  writeFailed:
    "Couldn't write the output file. Check that the output directory exists and that you have permission to write to it.",

  spriteMissing: (name: string) =>
    `Sprite "${name}" is listed in the config but wasn't found in the asset directory. Add the file, or remove the entry from the config.`,

  quotaHit:
    "Upload quota exceeded for this account. Wait for the quota to reset, or upgrade the plan, then retry.",

  sanityCheckFailed:
    "The packed atlas failed validation: sprite bounds fall outside the atlas. Re-run with --verbose to see the offending sprites.",
};

export const LOGS = {
  startup: "Starting the asset pipeline.",
  packing: "Packing the atlas.",
  done: "Finished. All assets are up to date.",
  retry: "Request failed. Retrying.",
};
