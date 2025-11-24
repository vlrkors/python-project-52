from whitenoise.storage import CompressedManifestStaticFilesStorage

# Allow missing manifest entries to fall back to the original filename in tests
CompressedManifestStaticFilesStorage.manifest_strict = False
