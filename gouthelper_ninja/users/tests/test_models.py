import pytest
from django.test import TestCase

from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.medhistorys.tests.factories import MedHistoryFactory
from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.models import Admin
from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.models import Provider
from gouthelper_ninja.users.models import User
from gouthelper_ninja.users.schema import PatientEditSchema
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory


class TestPatient(TestCase):
    def setUp(self):
        self.patient = PatientFactory()
        self.provider = UserFactory()

    def test__update(self):
        """Tests that the update method updates the patient and its related models."""

        data = PatientEditSchema(
            dateofbirth={"dateofbirth": "2000-01-01"},
            ethnicity={"ethnicity": Ethnicitys.KOREAN},
            gender={"gender": Genders.FEMALE},
            gout={"history_of": False},
            goutdetail={
                "at_goal": True,
                "at_goal_long_term": True,
                "flaring": False,
                "on_ppx": True,
                "on_ult": False,
                "starting_ult": True,
            },
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
        self.patient = PatientFactory()

    def test_user_get_absolute_url(self):
        assert self.user.get_absolute_url() == f"/users/{self.user.username}/"
        assert self.patient.get_absolute_url() == f"/users/patients/{self.patient.id}/"

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

    def test__creator(self):
        """Test that the creator property returns the user who created the user."""

        # Assert that a Patient whose initial history does not have a history_user
        # returns None for creator
        expected_num_histories = 2
        assert self.patient.history.count() == expected_num_histories
        assert self.patient.creator is None

        # Create a Patient with an initial history user
        patient_with_creator = PatientFactory(
            creator=self.user,
        )
        expected_num_histories = 2
        assert patient_with_creator.history.count() == expected_num_histories
        assert patient_with_creator.creator == self.user

        # For a Patient with multiple histories, only the first of which
        # has a history_user, should return the first history's user

        # Calling save() will create a new history entry
        patient_with_creator.save()

        # Expected number of histories is 3 due to the initial save,
        # the post-generation hook, and the save in the test
        expected_num_histories = 3
        assert patient_with_creator.history.count() == expected_num_histories
        delattr(patient_with_creator, "creator")  # Remove cached property
        assert patient_with_creator.creator == self.user

    def test_role_change_updates_class(self):
        """Tests that changing a user's role correctly updates
        the proxy model class after saving."""
        # Start with a Provider
        user = Provider.objects.create_user(
            username="billthedinosaur",
            email="test@example.com",
            password="password",  # noqa: S106
        )
        assert user.__class__ == Provider
        assert user.role == Roles.PROVIDER

        # Change role to ADMIN
        user.role = Roles.ADMIN
        user.save()

        assert user.role == Roles.ADMIN
        assert user.__class__ == Admin

        # Change role to PSEUDOPATIENT
        user.role = Roles.PSEUDOPATIENT
        user.save()

        assert user.role == Roles.PSEUDOPATIENT
        assert user.__class__ == Patient

        # Change back to PROVIDER
        user.role = Roles.PROVIDER
        user.save()

        assert user.role == Roles.PROVIDER
        assert user.__class__ == Provider

    def test_get_medhistory_returns_correct_instance(self):
        medhistory = MedHistoryFactory(patient=self.patient, mhtype=MHTypes.DIABETES)
        result = self.patient.get_medhistory(MHTypes.DIABETES)
        assert result == medhistory

    def test_get_medhistory_returns_none_if_not_exists(self):
        result = self.patient.get_medhistory(MHTypes.DIABETES)
        assert result is None

    def test_get_medhistory_raises_for_non_patient(self):
        provider = self.user
        with pytest.raises(AttributeError) as excinfo:
            provider.get_medhistory(MHTypes.DIABETES)
        assert "is not a Patient" in str(excinfo.value)

    def test_get_medhistory_with_pseudopatient_role(self):
        patient = PatientFactory(role=Roles.PSEUDOPATIENT)
        medhistory = MedHistoryFactory(patient=patient, mhtype=MHTypes.DIABETES)
        result = patient.get_medhistory(MHTypes.DIABETES)
        assert result == medhistory

    def test_get_medhistory_uses_medhistorys_qs_if_present(self):
        medhistory = MedHistoryFactory(patient=self.patient, mhtype=MHTypes.DIABETES)
        # Simulate a custom queryset attribute
        self.patient.medhistorys_qs = self.patient.medhistory_set.all()
        result = self.patient.get_medhistory(MHTypes.DIABETES)
        assert result == medhistory
