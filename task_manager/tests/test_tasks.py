import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse

from task_manager.statuses.models import Status
from task_manager.tasks.filters import TaskFilter
from task_manager.tasks.models import Task

User = get_user_model()


@pytest.mark.django_db
def test_task_filter_adds_form_select_class():
    # Проверяем, что TaskFilter добавляет bootstrap-класс ко всем полям выбора.
    TaskFilter(data={})
    form = TaskFilter(data={}).form
    for name in ("status", "executor", "labels"):
        field = form.fields[name]
        assert "form-select" in field.widget.attrs["class"]
    assert form.label_suffix == ""


@pytest.mark.django_db
def test_task_list_self_tasks_filter(client):
    status = Status.objects.create(name="Open")
    author = User.objects.create_user(username="author", password="pwd")
    other = User.objects.create_user(username="other", password="pwd")
    my_task = Task.objects.create(name="Mine", status=status, author=author)
    Task.objects.create(name="Foreign", status=status, author=other)

    client.login(username="author", password="pwd")
    response = client.get(reverse("tasks_index"), {"self_tasks": "1"})

    content = response.content.decode()
    assert response.status_code == 200
    assert my_task.name in content
    assert "Foreign" not in content


@pytest.mark.django_db
def test_task_delete_denied_for_non_author(client):
    status = Status.objects.create(name="Open")
    author = User.objects.create_user(username="author", password="pwd")
    User.objects.create_user(username="stranger", password="pwd")
    task = Task.objects.create(name="Protected", status=status, author=author)

    client.login(username="stranger", password="pwd")
    response = client.post(reverse("task_delete", args=[task.id]), follow=True)

    assert response.status_code == 200
    assert Task.objects.filter(id=task.id).exists()
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert messages  # должно быть сообщение об ошибке
    assert any(
        "author" in msg.lower() or "автор" in msg.lower()
        for msg in messages
    )


@pytest.mark.django_db
def test_task_create_sets_author(client):
    status = Status.objects.create(name="Open")
    user = User.objects.create_user(username="creator", password="pwd")
    client.login(username="creator", password="pwd")

    response = client.post(
        reverse("task_create"),
        {
            "name": "New task",
            "status": status.id,
            "executor": "",
            "description": "",
            "labels": [],
        },
        follow=True,
    )

    assert response.status_code == 200
    created = Task.objects.get(name="New task")
    assert created.author == user


@pytest.mark.django_db
def test_task_delete_requires_login(client):
    status = Status.objects.create(name="Open")
    author = User.objects.create_user(username="author", password="pwd")
    task = Task.objects.create(
        name="Auth required",
        status=status,
        author=author,
    )

    response = client.post(reverse("task_delete", args=[task.id]), follow=True)

    # Перенаправление на логин, задача не удалена.
    assert response.status_code == 200
    assert Task.objects.filter(id=task.id).exists()
