import pytest
from django.template import Context
from django.test import RequestFactory
from django.urls import reverse

from django import forms
from django_bootstrap5.templatetags.django_bootstrap5 import (
    bootstrap_field,
    bootstrap_form,
    bootstrap_messages,
)
from task_manager.labels.models import Label
from task_manager.tasks.models import Task
from task_manager.views import IndexView
from task_manager.rollbar_middleware import CustomRollbarNotifierMiddleware


@pytest.mark.django_db
def test_index_view_get():
    request = RequestFactory().get(reverse("index"))
    response = IndexView.as_view()(request)
    assert response.status_code == 200


def test_bootstrap_form_none_returns_empty():
    assert bootstrap_form(None) == ""


@pytest.mark.django_db
def test_bootstrap_field_renders_label_and_errors():
    class DummyForm(forms.Form):
        name = forms.CharField(help_text="help")

    form = DummyForm(data={"name": ""})
    assert not form.is_valid()
    bound_field = form["name"]

    html = bootstrap_field(bound_field, show_label=True).lower()
    assert "form-control" in html
    assert "help" in html
    assert ("required" in html) or ("обяз" in html)


def test_bootstrap_messages_with_no_request():
    assert bootstrap_messages({}) == ""


@pytest.mark.django_db
def test_model_str_methods():
    label = Label(name="Bug")
    task = Task(name="Task name")
    assert str(label) == "Bug"
    assert str(task) == "Task name"


def test_rollbar_middleware_calls_super_when_token(monkeypatch, settings):
    settings.ROLLBAR = {"access_token": "token", "environment": "test"}

    called = {}

    def fake_init(self, get_response=None):
        called["ran"] = True

    monkeypatch.setattr(
        "task_manager.rollbar_middleware.RollbarNotifierMiddleware.__init__",
        fake_init,
    )

    CustomRollbarNotifierMiddleware(lambda req: req)
    assert called.get("ran") is True
