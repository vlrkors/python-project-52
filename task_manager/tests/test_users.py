import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils.crypto import get_random_string

from task_manager.statuses.models import Status
from task_manager.tasks.models import Task
from task_manager.users.forms import UserCreateForm, UserUpdateForm

User = get_user_model()


@pytest.mark.django_db
def test_user_create_form_validation_errors():
    pwd1 = get_random_string(8)
    pwd2 = get_random_string(8)
    mismatch_form = UserCreateForm(
        data={
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "password1": pwd1,
            "password2": pwd2,
        }
    )
    assert not mismatch_form.is_valid()
    assert "не совпадают" in " ".join(mismatch_form.errors["password2"])

    short_form = UserCreateForm(
        data={
            "first_name": "John",
            "last_name": "Doe",
            "username": "john-short",
            "password1": get_random_string(2),
            "password2": get_random_string(2),
        }
    )
    assert not short_form.is_valid()
    assert any("3" in err for err in short_form.errors["password2"])


@pytest.mark.django_db
def test_user_create_form_calls_add_error_on_mismatch(monkeypatch):
    form = UserCreateForm(
        data={
            "first_name": "John",
            "last_name": "Doe",
            "username": "john-mismatch",
            "password1": "longpassword",
            "password2": "longpassworD",
        }
    )
    called = {}

    def tracker(field, message):
        called["called"] = True
        return orig_add_error(field, message)

    orig_add_error = form.add_error
    form.add_error = tracker
    assert not form.is_valid()
    assert called.get("called") is True


@pytest.mark.django_db
def test_user_update_form_allows_same_username():
    user = User.objects.create_user(
        username="same", password="pwd", first_name="A", last_name="B"
    )
    form = UserUpdateForm(
        instance=user,
        data={
            "first_name": "A",
            "last_name": "B",
            "username": "same",
            "password1": "pwd123",
            "password2": "pwd123",
        },
    )
    assert form.is_valid()
    assert form.cleaned_data["username"] == "same"


@pytest.mark.django_db
def test_user_update_form_allows_new_unique_username():
    user = User.objects.create_user(
        username="old", password="pwd", first_name="A", last_name="B"
    )
    form = UserUpdateForm(
        instance=user,
        data={
            "first_name": "A",
            "last_name": "B",
            "username": "newunique",
            "password1": "pwd123",
            "password2": "pwd123",
        },
    )
    assert form.is_valid()
    assert form.cleaned_data["username"] == "newunique"


@pytest.mark.django_db
def test_user_update_form_unique_username_validation():
    user = User.objects.create_user(
        username="johndoe", password="pwd", first_name="John", last_name="Doe"
    )
    other = User.objects.create_user(
        username="taken", password="pwd", first_name="Jane", last_name="Doe"
    )
    form = UserUpdateForm(
        instance=user,
        data={
            "first_name": "John",
            "last_name": "Doe",
            "username": other.username,
            "password1": "pwd123",
            "password2": "pwd123",
        },
    )
    assert not form.is_valid()
    username_errors = " ".join(form.errors["username"])
    assert "уже существует" in username_errors.lower()


@pytest.mark.django_db
def test_user_update_forbidden_for_another_user(client):
    user = User.objects.create_user(username="owner", password="pwd")
    User.objects.create_user(username="stranger", password="pwd")
    client.login(username="stranger", password="pwd")

    response = client.post(
        reverse("user_update", args=[user.id]),
        {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": "newname",
            "password1": "pwd123",
            "password2": "pwd123",
        },
        follow=True,
    )

    assert response.status_code == 200
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert any(
        "permission" in msg.lower() or "прав" in msg.lower()
        for msg in messages
    )
    user.refresh_from_db()
    assert user.username == "owner"


@pytest.mark.django_db
def test_user_delete_protected_when_used_in_task(client):
    status = Status.objects.create(name="Open")
    user = User.objects.create_user(username="owner", password="pwd")
    Task.objects.create(name="WithAuthor", status=status, author=user)

    client.login(username="owner", password="pwd")
    response = client.post(reverse("user_delete", args=[user.id]), follow=True)

    assert response.status_code == 200
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert any(
        "impossible to delete" in msg.lower()
        or "невозможно удалить" in msg.lower()
        for msg in messages
    )
    assert User.objects.filter(id=user.id).exists()


@pytest.mark.django_db
def test_user_delete_forbidden_for_other_user(client):
    owner = User.objects.create_user(username="owner", password="pwd")
    User.objects.create_user(username="other", password="pwd")
    client.login(username="other", password="pwd")

    response = client.post(reverse("user_delete", args=[owner.id]), follow=True)

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert any(
        "permission" in msg.lower() or "прав" in msg.lower()
        for msg in messages
    )
    assert User.objects.filter(id=owner.id).exists()


@pytest.mark.django_db
def test_login_view_redirects_to_index(client):
    password = "pwd123"
    user = User.objects.create_user(username="loginuser", password=password)
    response = client.post(
        reverse("login"),
        {"username": user.username, "password": password},
        follow=True,
    )
    assert any(reverse("index") == url for url, _ in response.redirect_chain)


@pytest.mark.django_db
def test_user_create_form_save_sets_password():
    form = UserCreateForm(
        data={
            "first_name": "Ann",
            "last_name": "Smith",
            "username": "ann",
            "password1": "secret",
            "password2": "secret",
        }
    )
    assert form.is_valid()
    user = form.save()
    assert user.check_password("secret")


@pytest.mark.django_db
def test_user_update_requires_login_message(client):
    user = User.objects.create_user(username="target", password="pwd")

    response = client.post(
        reverse("user_update", args=[user.id]),
        {
            "first_name": "",
            "last_name": "",
            "username": "target",
            "password1": "pwd123",
            "password2": "pwd123",
        },
        follow=True,
    )
    # Должен произойти редирект на логин из-за отсутствия авторизации.
    assert any("/login" in url for url, _ in response.redirect_chain)


@pytest.mark.django_db
def test_user_delete_requires_login_message(client):
    user = User.objects.create_user(username="target", password="pwd")

    response = client.post(reverse("user_delete", args=[user.id]), follow=True)
    assert any("/login" in url for url, _ in response.redirect_chain)


@pytest.mark.django_db
def test_user_logout_sets_message(client):
    User.objects.create_user(username="target", password="pwd")
    client.login(username="target", password="pwd")

    response = client.post(reverse("logout"), follow=True)
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert messages  # сообщение о выходе должно быть добавлено
