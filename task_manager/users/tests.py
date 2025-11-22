import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from task_manager.statuses.models import Status
from task_manager.tasks.models import Task
from task_manager.users.forms import UserRegistrationForm, UserUpdateForm

User = get_user_model()


@pytest.mark.django_db
class UserCrudTests(TestCase):
    fixtures = ["users.json"]

    def setUp(self):
        super().setUp()
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)

        for user in (self.user1, self.user2):
            user.set_password("testpass123")  # NOSONAR
            user.save()

    def test_user_registration_creates_account_and_redirects_to_login(self):
        users_before = User.objects.count()
        response = self.client.post(
            reverse("user_create"),
            {
                "username": "new_user",
                "first_name": "New",
                "last_name": "User",
                "password1": "newpass123",  # NOSONAR
                "password2": "newpass123",  # NOSONAR
            },
        )

        self.assertRedirects(response, reverse("login"))
        self.assertEqual(User.objects.count(), users_before + 1)
        self.assertTrue(User.objects.filter(username="new_user").exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertIn("User created successfully", str(messages[0]))

    def test_user_update_changes_profile_and_redirects_to_index(self):
        self.client.login(username="user1", password="testpass123")  # NOSONAR
        response = self.client.post(
            reverse("user_update", kwargs={"pk": self.user1.pk}),
            {
                "username": "user1",
                "first_name": "Updated",
                "last_name": "User",
                "password1": "newpass123",  # NOSONAR
                "password2": "newpass123",  # NOSONAR
            },
        )

        self.assertRedirects(response, reverse("users_index"))
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, "Updated")
        self.assertTrue(self.user1.check_password("newpass123"))

        messages = list(get_messages(response.wsgi_request))
        self.assertIn("User updated successfully", str(messages[0]))

    def test_user_delete_removes_user_and_redirects_to_index(self):
        self.client.login(username="user2", password="testpass123")  # NOSONAR
        response = self.client.post(
            reverse("user_delete", kwargs={"pk": self.user2.pk}),
            follow=False,
        )

        self.assertRedirects(response, reverse("users_index"))
        self.assertFalse(User.objects.filter(pk=self.user2.pk).exists())

    def test_user_with_tasks_cannot_be_deleted(self):
        status = Status.objects.create(name="Test status")
        Task.objects.create(
            name="Test task",
            status=status,
            author=self.user1,
        )

        self.client.login(username="user1", password="testpass123")  # NOSONAR
        response = self.client.post(
            reverse("user_delete", kwargs={"pk": self.user1.pk}),
            follow=True,
        )

        self.assertTrue(User.objects.filter(pk=self.user1.pk).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("It is impossible to delete the user", str(messages[0]))

    def test_user_update_requires_login(self):
        response = self.client.post(
            reverse("user_update", kwargs={"pk": self.user1.pk}),
            follow=True,
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("You are not logged in", str(messages[0]))

    def test_user_update_blocked_for_other_user(self):
        self.client.login(username="user2", password="testpass123")  # NOSONAR
        response = self.client.post(
            reverse("user_update", kwargs={"pk": self.user1.pk}),
            follow=True,
        )
        messages = list(get_messages(response.wsgi_request))
        expected_permission_message = (
            "You do not have permission to perform this action."
        )
        self.assertIn(expected_permission_message, str(messages[0]))

    def test_user_delete_requires_login(self):
        response = self.client.post(
            reverse("user_delete", kwargs={"pk": self.user1.pk}),
            follow=True,
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("You are not logged in", str(messages[0]))
        self.assertTrue(User.objects.filter(pk=self.user1.pk).exists())

    def test_user_delete_blocked_for_other_user(self):
        self.client.login(username="user1", password="testpass123")  # NOSONAR
        response = self.client.post(
            reverse("user_delete", kwargs={"pk": self.user2.pk}),
            follow=True,
        )
        messages = list(get_messages(response.wsgi_request))
        expected_permission_message = (
            "You do not have permission to perform this action."
        )
        self.assertIn(expected_permission_message, str(messages[0]))
        self.assertTrue(User.objects.filter(pk=self.user2.pk).exists())

    def test_login_redirects_to_index_and_sets_message(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "user1",
                "password": "testpass123",  # NOSONAR
            },
            follow=True,
        )
        self.assertEqual(response.wsgi_request.path, reverse("index"))
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("You are logged in", str(messages[0]))

    def test_logout_adds_message(self):
        self.client.login(username="user1", password="testpass123")  # NOSONAR
        response = self.client.post(reverse("logout"), follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("You are logged out", str(messages[0]))
        self.assertEqual(response.wsgi_request.path, reverse("index"))

    def test_registration_form_rejects_mismatched_passwords(self):
        form = UserRegistrationForm(
            data={
                "username": "newbie",
                "first_name": "New",
                "last_name": "User",
                "password1": "abc123",  # NOSONAR
                "password2": "cba123",  # NOSONAR
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
        self.assertIn("didn", "".join(form.errors["password2"]).lower())

    def test_registration_form_rejects_short_password(self):
        form = UserRegistrationForm(
            data={
                "username": "shorty",
                "first_name": "Short",
                "last_name": " User",
                "password1": "ab",  # NOSONAR
                "password2": "ab",  # NOSONAR
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("too short", str(form.errors))

    def test_update_form_prevents_duplicate_username(self):
        form = UserUpdateForm(
            instance=self.user1,
            data={
                "username": self.user2.username,
                "first_name": "User",
                "last_name": "One",
                "password1": "newpass123",  # NOSONAR
                "password2": "newpass123",  # NOSONAR
            },
        )
        self.assertFalse(form.is_valid())
        unique_message = str(
            User._meta.get_field("username").error_messages["unique"]
        )
        self.assertIn(unique_message, str(form.errors))

    def test_update_form_allows_same_username(self):
        form = UserUpdateForm(
            instance=self.user1,
            data={
                "username": self.user1.username,
                "first_name": "User",
                "last_name": "One",
                "password1": "abc",  # NOSONAR
                "password2": "abc",  # NOSONAR
            },
        )
        self.assertTrue(form.is_valid())
