import importlib
import os


def test_asgi_application_loads(monkeypatch):
    # Убедимся, что модуль загружается и устанавливает DJANGO_SETTINGS_MODULE
    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)
    module = importlib.reload(importlib.import_module("task_manager.asgi"))
    assert os.environ["DJANGO_SETTINGS_MODULE"] == "task_manager.settings"
    assert hasattr(module, "application")
