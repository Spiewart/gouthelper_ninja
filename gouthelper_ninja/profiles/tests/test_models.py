import pytest
from django.db import IntegrityError
from django.urls import reverse

from gouthelper_ninja.profiles.models import AdminProfile
from gouthelper_ninja.profiles.models import PatientProfile
from gouthelper_ninja.profiles.models import ProviderProfile
from gouthelper_ninja.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestAdminProfile:
    def test_str(self):
        user = UserFactory(username="admin_user")
        admin_profile = AdminProfile.objects.create(user=user)
        assert str(admin_profile) == "admin_user's Profile"

    def test_get_absolute_url(self):
        user = UserFactory(username="admin_user_url")
        admin_profile = AdminProfile.objects.create(user=user)
        expected_url = reverse("users:detail", kwargs={"username": user.username})
        assert admin_profile.get_absolute_url() == expected_url

    def test_history_creation(self):
        user = UserFactory()
        admin_profile = AdminProfile.objects.create(user=user)
        assert admin_profile.history.count() == 1
        admin_profile.user.name = "New Name"
        admin_profile.user.save()
        admin_profile.save()
        expected_history_count = 2
        assert admin_profile.history.count() == expected_history_count


class TestPatientProfile:
    def test_str(self):
        user = UserFactory(username="patient_user")
        patient_profile = PatientProfile.objects.create(user=user)
        assert str(patient_profile) == "patient_user's Profile"

    def test_get_absolute_url(self):
        user = UserFactory(username="patient_user_url")
        patient_profile = PatientProfile.objects.create(user=user)
        expected_url = reverse("users:detail", kwargs={"username": user.username})
        assert patient_profile.get_absolute_url() == expected_url

    def test_patient_profile_with_provider(self):
        patient_user = UserFactory(username="patient1")
        provider_user = UserFactory(username="provider1")
        patient_profile = PatientProfile.objects.create(
            user=patient_user,
            provider=provider_user,
            provider_alias=1,
        )
        assert patient_profile.provider == provider_user
        assert patient_profile.provider_alias == 1
        assert patient_profile.history.count() == 1

    def test_patient_profile_without_provider(self):
        patient_user = UserFactory(username="patient2")
        patient_profile = PatientProfile.objects.create(user=patient_user)
        assert patient_profile.provider is None
        assert patient_profile.provider_alias is None
        assert patient_profile.history.count() == 1

    def test_patient_profile_constraint_provider_alias_mismatch(self):
        """
        Tests that CheckConstraint %(class)s_alias_required_for_provider fails
        if provider is set and provider_alias is None.
        """
        patient_user = UserFactory(username="patient_constr_1")
        provider_user = UserFactory(username="provider_constr_1")
        with pytest.raises(
            IntegrityError,
        ) as excinfo:  # Using generic IntegrityError as DB backend might vary
            PatientProfile.objects.create(
                user=patient_user,
                provider=provider_user,
                provider_alias=None,
            )
        # Check if the constraint name is part of the error message
        assert (
            "patientprofile_alias_required_for_provider" in str(excinfo.value).lower()
        )

    def test_patient_profile_constraint_valid_no_provider(self):
        """
        Tests that CheckConstraint %(class)s_alias_required_for_provider passes
        if provider and provider_alias are both None.
        """
        patient_user = UserFactory(username="patient_constr_valid_1")
        try:
            PatientProfile.objects.create(
                user=patient_user,
                provider=None,
                provider_alias=None,
            )
        except IntegrityError:  # pragma: no cover
            pytest.fail(
                "Constraint failed for valid case: provider and alias are None.",
            )

    def test_patient_profile_constraint_valid_with_provider(self):
        """
        Tests that CheckConstraint %(class)s_alias_required_for_provider passes
        if provider and provider_alias are both set.
        """
        patient_user = UserFactory(username="patient_constr_valid_2")
        provider_user = UserFactory(username="provider_constr_valid_2")
        try:
            PatientProfile.objects.create(
                user=patient_user,
                provider=provider_user,
                provider_alias=1,
            )
        except IntegrityError:  # pragma: no cover  noqa: BLE001
            pytest.fail("Constraint failed for valid case: provider and alias are set.")


class TestProviderProfile:
    def test_str(self):
        user = UserFactory(username="provider_user")
        provider_profile = ProviderProfile.objects.create(user=user)
        assert str(provider_profile) == "provider_user's Profile"

    def test_get_absolute_url(self):
        user = UserFactory(username="provider_user_url")
        provider_profile = ProviderProfile.objects.create(user=user)
        expected_url = reverse("users:detail", kwargs={"username": user.username})
        assert provider_profile.get_absolute_url() == expected_url

    def test_history_creation(self):
        user = UserFactory()
        provider_profile = ProviderProfile.objects.create(user=user)
        assert provider_profile.history.count() == 1
        provider_profile.user.name = "New Provider Name"
        provider_profile.user.save()
        provider_profile.save()
        expected_history_count = 2
        assert provider_profile.history.count() == expected_history_count
