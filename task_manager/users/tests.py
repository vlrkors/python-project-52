import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from task_manager.statuses.models import Status
from task_manager.tasks.models import Task

User = get_user_model()


@pytest.mark.django_db
class UserCRUDTests(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.user3 = User.objects.get(pk=3)

        for user in [self.user1, self.user2, self.user3]:
            user.set_password('testpass123')
            user.save()

    def test_user_registration(self):
        initial_users = User.objects.count()

        url = reverse('user_create')
        data = {
            'username': 'newuser',
            'password1': 'newpass123',  # NOSONAR
            'password2': 'newpass123',  # NOSONAR
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), initial_users + 1)
        self.assertTrue(User.objects.filter(username='newuser').exists())

        messages = list(get_messages(response.wsgi_request))
        assert "успешно" in str(messages[0]).lower()

    def test_user_update_authenticated(self):
        self.client.login(username='user1', password='testpass123')  # NOSONAR
        url = reverse('user_update', kwargs={'pk': self.user1.pk})
        response = self.client.post(
            url,
            {
                'username': 'user1',  # NOSONAR
                'first_name': 'Updated',  # NOSONAR
                'last_name': 'User',  # NOSONAR
                'password1': 'newpass123',  # NOSONAR
                'password2': 'newpass123',  # NOSONAR
            }
        )
        self.assertRedirects(response, reverse('users_index'))
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'Updated')
        self.assertTrue(self.user1.check_password('newpass123'))

    def test_user_update_unauthenticated(self):
        url = reverse('user_update', kwargs={'pk': self.user1.pk})
        response = self.client.post(url)

        login_url = reverse('login')
        expected_redirect = f"{login_url}?next={url}"
        self.assertRedirects(response, expected_redirect)

        messages = list(get_messages(response.wsgi_request))
        assert "не авторизованы" in str(messages[0]).lower()

    def test_cannot_delete_user_with_tasks(self):
        status = Status.objects.create(name='В работе')

        Task.objects.create(
            name="Test task",
            status=status,
            author=self.user1
        )

        self.client.login(username='user1', password='testpass123')  # NOSONAR
        self.client.post(reverse('user_delete', args=[self.user1.pk]))

        self.assertTrue(User.objects.filter(pk=self.user1.pk).exists())