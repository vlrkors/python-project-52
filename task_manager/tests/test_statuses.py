import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse

from task_manager.statuses.models import Status
from task_manager.tasks.models import Task

User = get_user_model()


@pytest.mark.django_db
def test_status_delete_success(client):
    User.objects.create_user(username="owner", password="pwd")
    status = Status.objects.create(name="Temporary")
    client.login(username="owner", password="pwd")

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
    user = User.objects.create_user(username="owner", password="pwd")
    status = Status.objects.create(name="In use")
    Task.objects.create(name="Has status", status=status, author=user)
    client.login(username="owner", password="pwd")

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
