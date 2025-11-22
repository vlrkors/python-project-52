"""Pytest bootstrap helpers for running Django without pytest-django."""

import os
from pathlib import Path

import django
import pytest
from django.test import Client, TestCase, TransactionTestCase
from django.test.utils import (
    setup_databases,
    setup_test_environment,
    teardown_databases,
    teardown_test_environment,
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")
os.environ.setdefault(
    "TEST_DATABASE_URL",
    f"sqlite:///{Path(__file__).resolve().parent / 'test_db.sqlite3'}",
)
django.setup()


@pytest.fixture(scope="session", autouse=True)
def _django_test_environment(pytestconfig):
    if pytestconfig.pluginmanager.hasplugin("django"):
        # pytest-django сам управляет окружением/БД.
        yield
        return

    setup_test_environment()  # pragma: no cover
    db_cfg = setup_databases(verbosity=0, interactive=False)  # pragma: no cover
    try:
        yield
    finally:
        teardown_databases(db_cfg, verbosity=0)  # pragma: no cover
        teardown_test_environment()  # pragma: no cover


class _PytestTransactionTestCase(TransactionTestCase):
    reset_sequences = True


@pytest.fixture(autouse=True)
def django_db(request, pytestconfig, _django_test_environment):
    if pytestconfig.pluginmanager.hasplugin("django"):
        # Полностью полагаемся на фикстуры pytest-django.
        yield
        return

    test_class = getattr(request.node, "cls", None)
    if test_class and issubclass(test_class, TestCase):
        yield
        return

    helper = _PytestTransactionTestCase(
        methodName="__init__",
    )  # pragma: no cover
    helper._pre_setup()  # pragma: no cover
    try:
        yield
    finally:
        helper._post_teardown()  # pragma: no cover


@pytest.fixture
def client(django_db):
    return Client()


@pytest.fixture(scope="session", autouse=True)
def _close_db_connections():
    from django.db import connections

    yield
    connections.close_all()


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "django_db: Enable database access for the test.",
    )
