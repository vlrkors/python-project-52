import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.crypto import get_random_string

from task_manager.users.forms import UserCreateForm

User = get_user_model()


@pytest.mark.django_db
def test_user_create_form_mismatch_passwords():
    pwd1 = get_random_string(8)
    pwd2 = pwd1 + "x"
    form = UserCreateForm(
        data={
            "first_name": "Mismatch",
            "last_name": "User",
            "username": "mismatch",
            "password1": pwd1,
            "password2": pwd2,
        }
    )
    assert not form.is_valid()
    errors = " ".join(form.errors["password2"])
    assert "не совпадают" in errors or "match" in errors.lower()


@pytest.mark.django_db
def test_user_create_form_mismatch_add_error_called(monkeypatch):
    pwd1 = get_random_string(6)
    pwd2 = pwd1 + "y"
    form = UserCreateForm(
        data={
            "first_name": "Mismatch",
            "last_name": "Hook",
            "username": "mismatch_hook",
            "password1": pwd1,
            "password2": pwd2,
        }
    )
    called = {}

    def tracker(field, message):
        called["field"] = field
        called["message"] = message
        return orig_add_error(field, message)

    orig_add_error = form.add_error
    form.add_error = tracker
    assert not form.is_valid()
    assert called.get("field") == "password2"


@pytest.mark.django_db
def test_user_create_form_short_password():
    short_pwd = get_random_string(2)
    form = UserCreateForm(
        data={
            "first_name": "Short",
            "last_name": "User",
            "username": "shortpwd",
            "password1": short_pwd,
            "password2": short_pwd,
        }
    )
    assert not form.is_valid()
    errors = " ".join(form.errors["password2"])
    assert "3" in errors or "short" in errors.lower()


@pytest.mark.django_db
def test_user_create_form_too_short_add_error(monkeypatch):
    short_pwd = get_random_string(2)
    form = UserCreateForm(
        data={
            "first_name": "ShortAdd",
            "last_name": "Hook",
            "username": "short_add",
            "password1": short_pwd,
            "password2": short_pwd,
        }
    )
    called = {}

    def tracker(field, message):
        called.setdefault("calls", []).append((field, message))
        return orig_add_error(field, message)

    orig_add_error = form.add_error
    form.add_error = tracker
    assert not form.is_valid()
    assert any(field == "password2" for field, _ in called.get("calls", []))
    # Убеждаемся, что form.save не падает, даже если пароль был коротким.
    form.cleaned_data["password1"] = "valid_pwd"
    form.save(commit=False)


@pytest.mark.django_db
def test_user_create_form_short_and_mismatch_combined():
    form = UserCreateForm(
        data={
            "first_name": "Combo",
            "last_name": "User",
            "username": "combo",
            "password1": get_random_string(1),
            "password2": get_random_string(1),
        }
    )
    assert not form.is_valid()
    errors = " ".join(form.errors["password2"])
    assert errors
    assert ("не совпадают" in errors) or ("match" in errors.lower())
    assert ("3" in errors) or ("short" in errors.lower())


@pytest.mark.django_db
def test_user_delete_view_handle_no_permission(client):
    owner = User.objects.create_user(username="owner", password="pwd")
    User.objects.create_user(username="other", password="pwd")
    client.login(username="other", password="pwd")

    response = client.post(reverse("user_delete", args=[owner.id]), follow=True)
    assert response.status_code == 200
    assert User.objects.filter(id=owner.id).exists()
    assert any("/users/" in url for url, _ in response.redirect_chain)
