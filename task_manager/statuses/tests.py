import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse

from task_manager.tasks.models import Task

from .models import Status

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='user1',
        password='testpass123',  # NOSONAR
    )


@pytest.fixture
def auth_client(client, user):
    client.login(username=user.username, password='testpass123')  # NOSONAR
    return client


@pytest.mark.django_db
def test_create_status(auth_client):
    response = auth_client.post(
        reverse('status_create'),
        {'name': 'new'},
    )

    assert response.status_code == 302
    assert response.url == reverse('statuses_index')
    assert Status.objects.filter(name='new').exists()

    messages = list(get_messages(response.wsgi_request))
    assert any('Status successfully created' in str(message) for message in messages)


@pytest.mark.django_db
def test_update_status(auth_client):
    status = Status.objects.create(name='in_progress')

    response = auth_client.post(
        reverse('status_update', args=[status.pk]),
        {'name': 'testing'},
    )

    assert response.status_code == 302
    assert response.url == reverse('statuses_index')

    status.refresh_from_db()
    assert status.name == 'testing'

    messages = list(get_messages(response.wsgi_request))
    assert any('Status successfully changed' in str(message) for message in messages)


@pytest.mark.django_db
def test_delete_status(auth_client):
    status = Status.objects.create(name='done')

    response = auth_client.post(reverse('status_delete', args=[status.pk]))

    assert response.status_code == 302
    assert response.url == reverse('statuses_index')
    assert not Status.objects.filter(pk=status.pk).exists()


@pytest.mark.django_db
def test_status_list_requires_login(client):
    url = reverse('statuses_index')
    response = client.get(url)
    login_url = reverse('login')
    assert response.status_code == 302
    assert response.url == f'{login_url}?next={url}'


@pytest.mark.django_db
def test_cannot_delete_status_in_use(auth_client, user):
    status = Status.objects.create(name='in_progress')
    Task.objects.create(
        name='Test task',
        status=status,
        author=user,
    )

    response = auth_client.post(reverse('status_delete', args=[status.pk]), follow=True)

    assert Status.objects.filter(pk=status.pk).exists()

    messages = list(get_messages(response.wsgi_request))
    assert any('It is impossible to delete the status' in str(message) for message in messages)
