import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from task_manager.statuses.models import Status
from task_manager.tasks.models import Task

User = get_user_model()


@pytest.mark.django_db
class UserCrudTests(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        super().setUp()
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)

        for user in (self.user1, self.user2):
            user.set_password('testpass123')  # NOSONAR
            user.save()

    def test_user_registration_creates_account_and_redirects_to_login(self):
        users_before = User.objects.count()
        response = self.client.post(
            reverse('user_create'),
            {
                'username': 'new_user',
                'first_name': 'New',
                'last_name': 'User',
                'password1': 'newpass123',  # NOSONAR
                'password2': 'newpass123',  # NOSONAR
            },
        )

        self.assertRedirects(response, reverse('login'))
        self.assertEqual(User.objects.count(), users_before + 1)
        self.assertTrue(User.objects.filter(username='new_user').exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertIn('User created successfully', str(messages[0]))

    def test_user_update_changes_profile_and_redirects_to_index(self):
        self.client.login(username='user1', password='testpass123')  # NOSONAR
        response = self.client.post(
            reverse('user_update', kwargs={'pk': self.user1.pk}),
            {
                'username': 'user1',
                'first_name': 'Updated',
                'last_name': 'User',
                'password1': 'newpass123',  # NOSONAR
                'password2': 'newpass123',  # NOSONAR
            },
        )

        self.assertRedirects(response, reverse('users_index'))
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'Updated')
        self.assertTrue(self.user1.check_password('newpass123'))

        messages = list(get_messages(response.wsgi_request))
        self.assertIn('User updated successfully', str(messages[0]))

    def test_user_delete_removes_user_and_redirects_to_index(self):
        self.client.login(username='user2', password='testpass123')  # NOSONAR
        response = self.client.post(
            reverse('user_delete', kwargs={'pk': self.user2.pk}),
            follow=False,
        )

        self.assertRedirects(response, reverse('users_index'))
        self.assertFalse(User.objects.filter(pk=self.user2.pk).exists())

    def test_user_with_tasks_cannot_be_deleted(self):
        status = Status.objects.create(name='Test status')
        Task.objects.create(
            name='Test task',
            status=status,
            author=self.user1,
        )

        self.client.login(username='user1', password='testpass123')  # NOSONAR
        response = self.client.post(
            reverse('user_delete', kwargs={'pk': self.user1.pk}),
            follow=True,
        )

        self.assertTrue(User.objects.filter(pk=self.user1.pk).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('It is impossible to delete the user', str(messages[0]))
