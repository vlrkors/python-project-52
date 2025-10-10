import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from task_manager.tasks.models import Task

from .models import Status

User = get_user_model()


@pytest.mark.django_db
class TestStatusCRUD:
    @pytest.fixture
    def logged_client(self, client):
        User.objects.create_user(username='user1',
                                 password='testpass123')  # NOSONAR
        client.login(username='user1', password='testpass123')  # NOSONAR
        return client

    def test_create_status(self, logged_client):
        url = reverse('status_create')
        response = logged_client.post(url, {'name': 'Новый'})
        assert response.status_code == 302
        assert Status.objects.filter(name='Новый').exists()

    def test_update_status(self, logged_client):
        status = Status.objects.create(name='Старый')
        url = reverse('status_update', args=[status.pk])
        logged_client.post(url, {'name': 'Обновленный'})
        status.refresh_from_db()
        assert status.name == 'Обновленный'

    def test_delete_status(self, logged_client):
        status = Status.objects.create(name='Удалить')
        url = reverse('status_delete', args=[status.pk])
        logged_client.post(url)
        assert not Status.objects.filter(pk=status.pk).exists()

    def test_status_list_requires_login(self, client):
        url = reverse('statuses_index')
        response = client.get(url)
        assert response.status_code == 302

    def test_cannot_delete_status_in_use(self, logged_client):
        status = Status.objects.create(name='В работе')
        author = User.objects.get(username='user1')
        Task.objects.create(
            name='Test task',
            status=status,
            author=author
        )

        url = reverse('status_delete', args=[status.pk])
        response = logged_client.post(url)

        assert response.status_code == 302

        assert Status.objects.filter(pk=status.pk).exists()
