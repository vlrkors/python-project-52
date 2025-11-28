import pytest
from django import forms
from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

from task_manager.django_bootstrap5.templatetags import django_bootstrap5


class SampleForm(forms.Form):
    name = forms.CharField(
        label="Имя",
        help_text="Подсказка",
        required=True,
    )


@pytest.fixture
def message_request():
    request = RequestFactory().get("/")
    setattr(request, "session", {})
    storage = FallbackStorage(request)
    setattr(request, "_messages", storage)
    return request


def test_bootstrap_messages_renders_alert(message_request):
    messages.add_message(message_request, messages.INFO, "Hello!")
    rendered = django_bootstrap5.bootstrap_messages(
        {"request": message_request},
    )
    assert "alert-info" in rendered
    assert "Hello!" in rendered


def test_bootstrap_messages_without_request_returns_empty():
    rendered = django_bootstrap5.bootstrap_messages({})
    assert rendered == ""


def test_bootstrap_field_renders_label_help_and_errors():
    form = SampleForm(data={"name": ""})
    assert not form.is_valid()
    field = form["name"]

    rendered = django_bootstrap5.bootstrap_field(field, show_label=True)
    assert "form-label" in rendered
    assert "form-text" in rendered
    assert "text-danger" in rendered


def test_bootstrap_field_none_returns_empty():
    assert django_bootstrap5.bootstrap_field(None) == ""


def test_bootstrap_button_adds_default_class():
    rendered = django_bootstrap5.bootstrap_button(
        "Save",
        button_class="primary",
    )
    assert "btn primary" in rendered


def test_bootstrap_form_none_returns_empty():
    assert django_bootstrap5.bootstrap_form(None) == ""
