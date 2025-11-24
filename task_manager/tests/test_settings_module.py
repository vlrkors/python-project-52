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
