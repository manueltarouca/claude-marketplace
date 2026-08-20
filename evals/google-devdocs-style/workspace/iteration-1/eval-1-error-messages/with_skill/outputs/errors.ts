// Error and log messages for the asset pipeline CLI.

export const ERRORS = {
  missingConfig:
    "Can't find a pipeline config file. Create one in the project root, or pass its path with --config.",

  badYaml:
    "Can't parse the pipeline config: the YAML is invalid. Check the file for wrong indentation or unquoted values, then run the command again.",

  noAssetDir:
    "No asset directory given. Pass the directory that holds the source sprites as the first argument.",

  atlasTooBig:
    "The sprites don't fit in one atlas at the configured maximum texture size. Remove sprites, reduce the padding, or raise the maximum size in the config, then pack again.",

  badChannel:
    "Unknown upload channel. Use one of the channels listed in the config, then run the command again.",

  authExpired:
    "Your upload credentials have expired. Sign in again, then retry the upload.",

  writeFailed:
    "Can't write the output file. Check that the output directory exists and that you have permission to write to it.",

  spriteMissing: (name: string) =>
    `Can't find the sprite ${name} in the asset directory. Add the file, or correct its name in the config.`,

  quotaHit:
    "You've reached your upload quota, so the upload stopped. Free up quota or upgrade your plan, then run the command again.",

  sanityCheckFailed:
    "The atlas failed its validation check: the frame data doesn't match the packed image. Delete the output atlas and pack it again. If the check still fails, report the issue.",
};

export const LOGS = {
  startup: "Starting the asset pipeline.",
  packing: "Packing the atlas.",
  done: "Finished. The pipeline wrote the atlas to the output directory.",
  retry: "Retrying.",
};
