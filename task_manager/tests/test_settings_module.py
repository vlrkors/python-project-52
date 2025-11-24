import importlib.util
from pathlib import Path

from task_manager import settings


def _load_settings_copy(monkeypatch, env):
    for key, value in env.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)

    spec = importlib.util.spec_from_file_location(
        "task_manager_settings_copy",
        Path(settings.BASE_DIR) / "task_manager" / "settings.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_to_bool_variants():
    assert settings._to_bool("True") is True
    assert settings._to_bool("1") is True
    assert settings._to_bool("yes") is True
    assert settings._to_bool("false") is False
    assert settings._to_bool(None, default=True) is True


def test_sqlite_db_config_windows_path(monkeypatch):
    monkeypatch.setattr(settings.os, "name", "nt")
    cfg = settings._sqlite_db_config("sqlite:///C:/tmp/db.sqlite3")
    assert cfg["ENGINE"] == "django.db.backends.sqlite3"
    assert cfg["NAME"] == "C:/tmp/db.sqlite3"


def test_sqlite_db_config_defaults_to_base(monkeypatch):
    monkeypatch.setattr(settings.os, "name", "posix")
    cfg = settings._sqlite_db_config("sqlite://")
    assert cfg["NAME"].endswith("db.sqlite3")


def test_static_storage_switches_in_testing(monkeypatch):
    module = _load_settings_copy(
        monkeypatch,
        {"PYTEST_RUNNING": "true", "DEBUG": None},
    )
    backend = module.STORAGES["staticfiles"]["BACKEND"]
    assert backend == "django.contrib.staticfiles.storage.StaticFilesStorage"


def test_allowed_hosts_and_csrf_from_env(monkeypatch):
    module = _load_settings_copy(
        monkeypatch,
        {
            "ALLOWED_HOSTS": "example.com,.foo.com",
            "CSRF_TRUSTED_ORIGINS": "https://custom.local",
        },
    )
    assert "example.com" in module.ALLOWED_HOSTS
    assert ".foo.com" in module.ALLOWED_HOSTS
    csrf = set(module.CSRF_TRUSTED_ORIGINS)
    assert "https://example.com" in csrf
    assert "https://foo.com" in csrf or "https://*.foo.com" in csrf
    assert "https://custom.local" in csrf


def test_host_to_csrf_origins_empty_and_dot():
    assert settings._host_to_csrf_origins("") == set()
    assert settings._host_to_csrf_origins(".") == set()


def test_database_sqlite_branch(monkeypatch):
    monkeypatch.setattr(settings.sys, "argv", ["manage.py"])
    module = _load_settings_copy(
        monkeypatch,
        {
            "PYTEST_RUNNING": None,
            "PYTEST_CURRENT_TEST": None,
            "DATABASE_URL": f"sqlite:///{settings.BASE_DIR / 'custom.sqlite3'}",
        },
    )
    assert module.DATABASES["default"]["NAME"].endswith("custom.sqlite3")


def test_database_non_sqlite_branch(monkeypatch):
    monkeypatch.setattr(settings.sys, "argv", ["manage.py"])

    class DummyDjDatabaseURL:
        @staticmethod
        def parse(url, conn_max_age, ssl_require):
            return {
                "URL": url,
                "AGE": conn_max_age,
                "SSL": ssl_require,
                "NAME": "parsed",
            }

    monkeypatch.setitem(
        settings.sys.modules,
        "dj_database_url",
        DummyDjDatabaseURL,
    )
    module = _load_settings_copy(
        monkeypatch,
        {
            "PYTEST_RUNNING": None,
            "PYTEST_CURRENT_TEST": None,
            "DATABASE_URL": "postgres://user:pass@localhost/db",
        },
    )
    assert module.DATABASES["default"]["NAME"] == "parsed"


def test_rollbar_not_configured_without_token(monkeypatch):
    module = _load_settings_copy(
        monkeypatch,
        {
            "ROLLBAR_ACCESS_TOKEN": None,
            "ROLLBAR_ENV": None,
            "ROLLBAR_CODE_VERSION": None,
        },
    )
    assert module.ROLLBAR is None
    assert (
        "task_manager.rollbar_middleware.CustomRollbarNotifierMiddleware"
        not in module.MIDDLEWARE
    )


def test_rollbar_configured_with_token(monkeypatch):
    module = _load_settings_copy(
        monkeypatch,
        {
            "ROLLBAR_ACCESS_TOKEN": "token-123",
            "ROLLBAR_ENV": "test-env",
            "ROLLBAR_CODE_VERSION": "1.2.3",
        },
    )
    assert module.ROLLBAR["access_token"] == "token-123"
    assert module.ROLLBAR["environment"] == "test-env"
    assert module.ROLLBAR["code_version"] == "1.2.3"
    assert (
        "task_manager.rollbar_middleware.CustomRollbarNotifierMiddleware"
        in module.MIDDLEWARE
    )
