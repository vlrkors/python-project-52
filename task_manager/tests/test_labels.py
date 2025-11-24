import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.crypto import get_random_string

from task_manager.labels.models import Label
from task_manager.statuses.models import Status
from task_manager.tasks.models import Task

User = get_user_model()


@pytest.mark.django_db
class TestLabelCRUD:
    @pytest.fixture
    def user(self):
        password = "pass_" + get_random_string(8)
        user = User.objects.create_user(
            username='testuser',
            password=password,
        )
        user.raw_password = password
        return user

    @pytest.fixture
    def logged_client(self, client, user):
        client.login(username='testuser', password=user.raw_password)
        return client

    @pytest.fixture
    def label(self):
        return Label.objects.create(name='Bug')

    def test_list_labels(self, logged_client, label):
        response = logged_client.get(reverse('labels_index'))
        assert response.status_code == 200
        assert 'Bug' in response.content.decode()

    def test_create_label(self, logged_client):
        response = logged_client.post(
            reverse('label_create'),
            {'name': 'Feature'},
        )
        assert response.status_code == 302
        assert Label.objects.filter(name='Feature').exists()

    def test_update_label(self, logged_client, label):
        response = logged_client.post(
            reverse('label_update', args=[label.id]),
            {'name': 'Hotfix'},
        )
        assert response.status_code == 302
        label.refresh_from_db()
        assert label.name == 'Hotfix'

    def test_delete_unused_label(self, logged_client, label):
        response = logged_client.post(reverse('label_delete', args=[label.id]))
        assert response.status_code == 302
        assert not Label.objects.filter(id=label.id).exists()

    def test_delete_used_label_is_protected(self, logged_client, label, user):
        status = Status.objects.create(name='В работе')
        task = Task.objects.create(name='Fix bug', author=user, status=status)
        task.labels.add(label)

        response = logged_client.post(reverse('label_delete', args=[label.id]))
        assert response.status_code == 302
        assert Label.objects.filter(id=label.id).exists()

    def test_label_str(self, label):
        assert str(label) == 'Bug'

    def test_create_duplicate_label_shows_error(self, logged_client, label):
        response = logged_client.post(
            reverse('label_create'),
            {'name': label.name},
        )
        assert response.status_code == 200
        assert Label.objects.filter(name=label.name).count() == 1


@pytest.mark.django_db
def test_labels_requires_login(client):
    response = client.get(reverse('labels_index'))
    # Должен редиректить на страницу логина
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_label_create_requires_login(client):
    response = client.post(
        reverse('label_create'),
        {'name': 'NeedAuth'},
        follow=True,
    )
    assert response.status_code == 200
    assert reverse('login') in response.redirect_chain[0][0]


@pytest.mark.django_db
def test_label_update_requires_login(client):
    label_obj = Label.objects.create(name='Temp')
    response = client.post(
        reverse('label_update', args=[label_obj.id]),
        {'name': 'X'},
        follow=True,
    )
    assert response.status_code == 200
    assert reverse('login') in response.redirect_chain[0][0]


@pytest.mark.django_db
def test_label_delete_requires_login(client):
    label_obj = Label.objects.create(name='TempDel')
    response = client.post(
        reverse('label_delete', args=[label_obj.id]),
        follow=True,
    )
    assert response.status_code == 200
    assert reverse('login') in response.redirect_chain[0][0]
    assert Label.objects.filter(id=label_obj.id).exists()
