from django.test import TestCase

from gouthelper_ninja.users.models import User


class TestUser(TestCase):
    """Tests for the User model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",  # noqa: S106
        )

    def test_user_get_absolute_url(self):
        assert self.user.get_absolute_url() == f"/users/{self.user.username}/"

    def test_default_user_role_provider(self):
        assert self.user.role == User.Roles.PROVIDER

    def test_default_superuser_role_admin(self):
        """Test that creating a superuser sets the superuser's role to
        Roles.ADMIN."""
        superuser = User.objects.create_superuser(
            username="superuser",
            email="blahbloo",
            password="blahblah",  # noqa: S106
        )
        assert superuser.role == User.Roles.ADMIN
