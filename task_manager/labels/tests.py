import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from task_manager.labels.models import Label
from task_manager.statuses.models import Status
from task_manager.tasks.models import Task

User = get_user_model()


@pytest.mark.django_db
class TestLabelViews:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username='testuser', password='password123'
            )

    @pytest.fixture
    def logged_client(self, client, user):
        client.login(username='testuser', password='password123')
        return client

    @pytest.fixture
    def label(self):
        return Label.objects.create(name='Bug')

    def test_label_list_view(self, logged_client, label):
        response = logged_client.get(reverse('labels_index'))
        assert response.status_code == 200
        assert 'Bug' in response.content.decode()

    def test_create_label(self, logged_client):
        response = logged_client.post(
            reverse('label_create'),
            {'name': 'Feature'}
            )
        assert response.status_code == 302
        assert Label.objects.filter(name='Feature').exists()

    def test_update_label(self, logged_client, label):
        response = logged_client.post(
            reverse('label_update', args=[label.id]),
            {'name': 'Hotfix'}
            )
        assert response.status_code == 302
        label.refresh_from_db()
        assert label.name == 'Hotfix'

    def test_delete_unused_label(self, logged_client, label):
        response = logged_client.post(reverse('label_delete', args=[label.id]))
        assert response.status_code == 302
        assert not Label.objects.filter(id=label.id).exists()

    def test_delete_used_label_protected(self, logged_client, label, user):
        status = Status.objects.create(name='На паузе')
        task = Task.objects.create(name='Fix bug', author=user, status=status)
        task.labels.add(label)

        response = logged_client.post(reverse('label_delete', args=[label.id]))
        assert response.status_code == 302
        assert Label.objects.filter(id=label.id).exists()