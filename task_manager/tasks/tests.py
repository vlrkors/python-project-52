import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse

from task_manager.statuses.models import Status

from .models import Task

User = get_user_model()


@pytest.mark.django_db
class TestTaskCRUD:
    def setup_method(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'  # NOSONAR
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123'  # NOSONAR
        )
        self.status = Status.objects.create(name='Новый')

    def test_create_task(self, client):
        client.login(username='user1', password='pass123')  # NOSONAR
        url = reverse('task_create')
        data = {
            'name': 'Test Task',
            'description': 'Some description',
            'status': self.status.id,
            'executor': self.user2.id
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert Task.objects.count() == 1
        assert Task.objects.first().author == self.user1

    def test_update_task(self, client):
        task = Task.objects.create(
            name='Old Task', status=self.status,
            author=self.user1
        )
        client.login(username='user1', password='pass123')  # NOSONAR
        url = reverse('task_update', kwargs={'pk': task.id})
        response = client.post(url, {
            'name': 'Updated Task',
            'description': '',
            'status': self.status.id
        })
        assert response.status_code == 302
        task.refresh_from_db()
        assert task.name == 'Updated Task'

    def test_delete_task_by_author(self, client):
        task = Task.objects.create(
            name='Task', status=self.status,
            author=self.user1
        )
        client.login(username='user1', password='pass123')  # NOSONAR
        url = reverse('task_delete', kwargs={'pk': task.id})
        response = client.post(url)
        assert response.status_code == 302
        assert Task.objects.count() == 0

    def test_delete_task_by_non_author(self, client):
        task = Task.objects.create(
            name='Task', status=self.status,
            author=self.user1
        )
        client.login(username='user2', password='pass123')  # NOSONAR
        url = reverse('task_delete', kwargs={'pk': task.id})
        response = client.post(url)
        assert Task.objects.count() == 1
        messages = list(get_messages(response.wsgi_request))
        assert "только ее автор" in str(messages[0])
