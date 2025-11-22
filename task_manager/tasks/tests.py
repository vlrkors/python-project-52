import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse

from task_manager.labels.models import Label
from task_manager.statuses.models import Status

from .models import Task

User = get_user_model()


@pytest.mark.django_db
class TestTaskCRUD:
    def setup_method(self):
        self.user1 = User.objects.create_user(
            username="user1",
            password="pass123",  # NOSONAR
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="pass123",  # NOSONAR
        )
        self.status = Status.objects.create(name="in_progress")
        self.label_bug = Label.objects.create(name="Bug")
        self.label_feature = Label.objects.create(name="Feature")

    def test_create_task(self, client):
        client.login(username="user1", password="pass123")  # NOSONAR
        url = reverse("task_create")
        data = {
            "name": "Test Task",
            "description": "Some description",
            "status": self.status.id,
            "executor": self.user2.id,
            "labels": [self.label_bug.id, self.label_feature.id],
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert Task.objects.count() == 1
        task = Task.objects.first()
        assert task.author == self.user1
        assert set(task.labels.values_list("id", flat=True)) == {
            self.label_bug.id,
            self.label_feature.id,
        }

    def test_update_task(self, client):
        task = Task.objects.create(
            name="Old Task",
            status=self.status,
            author=self.user1,
        )
        task.labels.add(self.label_bug)
        client.login(username="user1", password="pass123")  # NOSONAR
        url = reverse("task_update", kwargs={"pk": task.id})
        response = client.post(
            url,
            {
                "name": "Updated Task",
                "description": "",
                "status": self.status.id,
                "executor": self.user2.id,
                "labels": [self.label_feature.id],
            },
        )
        assert response.status_code == 302
        task.refresh_from_db()
        assert task.name == "Updated Task"
        assert list(task.labels.values_list("id", flat=True)) == [
            self.label_feature.id
        ]

    def test_delete_task_by_author(self, client):
        task = Task.objects.create(
            name="Task",
            status=self.status,
            author=self.user1,
        )
        client.login(username="user1", password="pass123")  # NOSONAR
        url = reverse("task_delete", kwargs={"pk": task.id})
        response = client.post(url)
        assert response.status_code == 302
        assert Task.objects.count() == 0

    def test_delete_task_by_non_author(self, client):
        task = Task.objects.create(
            name="Task",
            status=self.status,
            author=self.user1,
        )
        client.login(username="user2", password="pass123")  # NOSONAR
        url = reverse("task_delete", kwargs={"pk": task.id})
        response = client.post(url)
        assert Task.objects.count() == 1
        messages = list(get_messages(response.wsgi_request))
        assert "Only the author can delete an issue." in str(messages[0])

    def test_delete_task_requires_authentication(self, client):
        task = Task.objects.create(
            name="Task",
            status=self.status,
            author=self.user1,
        )
        url = reverse("task_delete", kwargs={"pk": task.id})
        response = client.post(url, follow=True)
        assert Task.objects.count() == 1
        assert response.redirect_chain  # redirected to login

    def test_filter_tasks_by_status_executor_label(self, client):
        status_done = Status.objects.create(name="done")
        task_with_label = Task.objects.create(
            name="Bugfix",
            status=self.status,
            author=self.user1,
            executor=self.user2,
        )
        task_with_label.labels.add(self.label_bug)

        other_task = Task.objects.create(
            name="Feature",
            status=status_done,
            author=self.user1,
            executor=self.user2,
        )
        other_task.labels.add(self.label_feature)

        client.login(username="user1", password="pass123")  # NOSONAR
        url = reverse("tasks_index")
        response = client.get(
            url,
            {
                "status": self.status.id,
                "executor": self.user2.id,
                "labels": self.label_bug.id,
                "self_tasks": "on",
            },
        )

        assert response.status_code == 200
        tasks = list(response.context_data["tasks"])
        assert tasks == [task_with_label]

    def test_filter_tasks_only_user_tasks(self, client):
        own_task = Task.objects.create(
            name="Own Task",
            status=self.status,
            author=self.user1,
        )
        Task.objects.create(
            name="Someone Task",
            status=self.status,
            author=self.user2,
        )

        client.login(username="user1", password="pass123")  # NOSONAR
        url = reverse("tasks_index")
        response = client.get(url, {"self_tasks": "on"})

        assert response.status_code == 200
        tasks = list(response.context_data["tasks"])
        assert tasks == [own_task]

    def test_task_str_returns_name(self):
        task = Task(
            name="Pretty name",
            status=self.status,
            author=self.user1,
        )
        assert str(task) == "Pretty name"
