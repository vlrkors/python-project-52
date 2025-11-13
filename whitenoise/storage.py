from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class CompressedManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """Заглушка, повторяющая интерфейс реального хранилища."""

    manifest_strict = False

    def stored_name(self, name, *args, **kwargs):
        try:
            return super().stored_name(name, *args, **kwargs)
        except Exception:
            # Не пытаемся искать отпечаток файла — просто возвращаем исходный путь.
            return name
