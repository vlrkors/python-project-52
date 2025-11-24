import importlib
import os


def test_wsgi_application_loads(monkeypatch):
    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)
    module = importlib.reload(importlib.import_module("task_manager.wsgi"))
    assert os.environ["DJANGO_SETTINGS_MODULE"] == "task_manager.settings"
    assert hasattr(module, "application")


def test_wsgi_application_is_callable():
    module = importlib.import_module("task_manager.wsgi")
    app = getattr(module, "application", None)
    assert app is not None
    assert callable(app)
