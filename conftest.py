"""Pytest bootstrap helpers for running Django without pytest-django."""
import os

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
django.setup()


@pytest.fixture(scope="session", autouse=True)
def _django_test_environment():
    setup_test_environment()
    db_cfg = setup_databases(verbosity=0, interactive=False)
    try:
        yield
    finally:
        teardown_databases(db_cfg, verbosity=0)
        teardown_test_environment()


class _PytestTransactionTestCase(TransactionTestCase):
    reset_sequences = True


@pytest.fixture(autouse=True)
def django_db(request, _django_test_environment):
    test_class = getattr(request.node, "cls", None)
    if test_class and issubclass(test_class, TestCase):
        yield
        return

    helper = _PytestTransactionTestCase(methodName="__init__")
    helper._pre_setup()
    try:
        yield
    finally:
        helper._post_teardown()


@pytest.fixture
def client(django_db):
    return Client()


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "django_db: Enable database access for the test.",
    )
