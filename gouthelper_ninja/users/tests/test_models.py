from django.test import TestCase

from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.users.models import User
from gouthelper_ninja.users.schema import PatientEditSchema
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory


class TestPatient(TestCase):
    def setUp(self):
        self.patient = PatientFactory()
        self.provider = UserFactory()

    def test__editors(self):
        """Test that the editors property returns a list of users who can edit the
        patient."""
        with self.assertNumQueries(1):
            assert isinstance(self.patient.editors, list)
            assert len(self.patient.editors) == 0
            assert self.patient.creator is None

        delattr(self.patient, "editors")

        last_history = self.patient.history.first()
        last_history.history_user = self.patient
        last_history.save()

        with self.assertNumQueries(1):
            assert self.patient.editors == [self.patient]
            assert self.patient.creator == self.patient

        self.patient.save()

        assert len(self.patient.editors) == 1

        delattr(self.patient, "editors")

        last_history = self.patient.history.first()

        last_history.history_user = self.provider
        last_history.save()

        with self.assertNumQueries(1):
            assert self.patient.editors == [self.patient, self.provider]
            assert self.patient.creator == self.patient

    def test__creator(self):
        """Test that the creator property returns the user who created the patient."""
        with self.assertNumQueries(1):
            assert self.patient.creator is None

        delattr(self.patient, "editors")

        last_history = self.patient.history.first()
        last_history.history_user = self.patient
        last_history.save()

        with self.assertNumQueries(1):
            assert self.patient.creator == self.patient

        self.patient.save()

        delattr(self.patient, "editors")

        last_history = self.patient.history.first()
        last_history.history_user = self.provider
        last_history.save()

        with self.assertNumQueries(1):
            assert self.patient.creator == self.patient

    def test__update(self):
        """Tests that the update method updates the patient and its related models."""

        data = PatientEditSchema(
            dateofbirth={"dateofbirth": "2000-01-01"},
            ethnicity={"ethnicity": Ethnicitys.KOREAN},
            gender={"gender": Genders.FEMALE},
        )
        patient = self.patient.update(data=data)
        assert patient.dateofbirth.dateofbirth.strftime("%Y-%m-%d") == "2000-01-01"
        assert patient.ethnicity.ethnicity == Ethnicitys.KOREAN
        assert patient.gender.gender == Genders.FEMALE


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
