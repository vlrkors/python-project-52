import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse

from task_manager.statuses.models import Status
from task_manager.tasks.models import Task
from task_manager.users.forms import UserCreateForm, UserUpdateForm

User = get_user_model()


@pytest.mark.django_db
def test_user_create_form_validation_errors():
    mismatch_form = UserCreateForm(
        data={
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "password1": "12",
            "password2": "21",
        }
    )
    assert not mismatch_form.is_valid()
    assert "не совпадают" in " ".join(mismatch_form.errors["password2"])

    short_form = UserCreateForm(
        data={
            "first_name": "John",
            "last_name": "Doe",
            "username": "john-short",
            "password1": "12",
            "password2": "12",
        }
    )
    assert not short_form.is_valid()
    assert any("3" in err for err in short_form.errors["password2"])


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
    other = User.objects.create_user(username="stranger", password="pwd")
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
    assert any("permission" in msg.lower() or "прав" in msg.lower() for msg in messages)
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
    assert any("impossible to delete" in msg.lower() or "невозможно удалить" in msg.lower() for msg in messages)
    assert User.objects.filter(id=user.id).exists()
