import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils.crypto import get_random_string

from task_manager.statuses.models import Status
from task_manager.tasks.models import Task

User = get_user_model()


@pytest.mark.django_db
def test_status_delete_success(client):
    password = get_random_string(8)
    User.objects.create_user(username="owner", password=password)
    status = Status.objects.create(name="Temporary")
    client.login(username="owner", password=password)

    response = client.post(
        reverse("status_delete", args=[status.id]),
        follow=True,
    )

    assert response.status_code == 200
    assert not Status.objects.filter(id=status.id).exists()
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert any(
        "successfully deleted" in msg.lower() or "успешно" in msg.lower()
        for msg in messages
    )


@pytest.mark.django_db
def test_status_delete_protected(client):
    password = get_random_string(8)
    user = User.objects.create_user(username="owner", password=password)
    status = Status.objects.create(name="In use")
    Task.objects.create(name="Has status", status=status, author=user)
    client.login(username="owner", password=password)

    response = client.post(
        reverse("status_delete", args=[status.id]),
        follow=True,
    )

    assert response.status_code == 200
    assert Status.objects.filter(id=status.id).exists()
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert any(
        "impossible to delete the status" in msg.lower()
        or "невозможно удалить статус" in msg.lower()
        for msg in messages
    )


@pytest.mark.django_db
def test_status_requires_login(client):
    response = client.get(reverse("statuses_index"))
    assert response.status_code == 302
    assert reverse("login") in response.url


@pytest.mark.django_db
def test_status_list_shows_items(client):
    password = get_random_string(8)
    User.objects.create_user(username="viewer", password=password)
    Status.objects.create(name="Visible")
    client.login(username="viewer", password=password)

    response = client.get(reverse("statuses_index"))
    assert response.status_code == 200
    assert "Visible" in response.content.decode()


@pytest.mark.django_db
def test_status_create_success(client):
    password = get_random_string(8)
    User.objects.create_user(username="owner", password=password)
    client.login(username="owner", password=password)

    response = client.post(
        reverse("status_create"),
        {"name": "NewStatus"},
        follow=True,
    )

    assert response.status_code == 200
    assert Status.objects.filter(name="NewStatus").exists()
    messages = [m.message.lower() for m in get_messages(response.wsgi_request)]
    assert any(
        "successfully created" in msg or "успешно" in msg
        for msg in messages
    )


@pytest.mark.django_db
def test_status_update_success(client):
    password = get_random_string(8)
    User.objects.create_user(username="owner", password=password)
    client.login(username="owner", password=password)
    status = Status.objects.create(name="Old")

    response = client.post(
        reverse("status_update", args=[status.id]),
        {"name": "Updated"},
        follow=True,
    )

    assert response.status_code == 200
    status.refresh_from_db()
    assert status.name == "Updated"
    messages = [m.message.lower() for m in get_messages(response.wsgi_request)]
    assert any(
        "successfully changed" in msg or "успешно" in msg
        for msg in messages
    )
