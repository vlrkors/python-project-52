import pytest
from django.contrib.auth import get_user_model

from task_manager.statuses.models import Status

from .forms import TaskForm
from .models import Task

User = get_user_model()


@pytest.mark.django_db
def test_task_form_has_bootstrap_classes():
    form = TaskForm()
    for field_name in ("name", "description"):
        cls = form.fields[field_name].widget.attrs.get("class", "")
        assert "form-control" in cls
    for field_name in ("status", "executor", "labels"):
        cls = form.fields[field_name].widget.attrs.get("class", "")
        assert "form-select" in cls


@pytest.mark.django_db
def test_task_form_validation_requires_status_and_name():
    form = TaskForm(data={"name": "", "description": ""})
    assert not form.is_valid()
    assert "status" in form.errors
    assert "name" in form.errors


@pytest.mark.django_db
def test_task_str_returns_name():
    status = Status.objects.create(name="In progress")
    user = User.objects.create_user(username="author", password="pwd")
    task = Task.objects.create(name="My task", status=status, author=user)
    assert str(task) == "My task"
