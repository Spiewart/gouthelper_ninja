import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.rules import add_provider_patient
from gouthelper_ninja.users.rules import change_patient
from gouthelper_ninja.users.rules import change_user
from gouthelper_ninja.users.rules import delete_patient
from gouthelper_ninja.users.rules import delete_user
from gouthelper_ninja.users.rules import obj_is_patient_or_pseudopatient
from gouthelper_ninja.users.rules import obj_without_creator
from gouthelper_ninja.users.rules import obj_without_provider
from gouthelper_ninja.users.rules import user_id_is_obj
from gouthelper_ninja.users.rules import user_is_a_provider
from gouthelper_ninja.users.rules import user_is_admin
from gouthelper_ninja.users.rules import user_is_anonymous
from gouthelper_ninja.users.rules import user_is_obj
from gouthelper_ninja.users.rules import user_is_obj_creator
from gouthelper_ninja.users.rules import user_is_obj_provider
from gouthelper_ninja.users.rules import user_username_is_obj
from gouthelper_ninja.users.rules import view_patient
from gouthelper_ninja.users.rules import view_user
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestPatientPredicates(TestCase):
    def setUp(self):
        """Create a User with the Provider role."""
        self.provider = UserFactory()
        self.admin = UserFactory(role=Roles.ADMIN)
        self.patient = PatientFactory()
        self.provider_patient = PatientFactory(provider=self.provider)
        self.anon = AnonymousUser()
        self.pseudopatient = PatientFactory(role=Roles.PSEUDOPATIENT)

    def test__user_id_is_obj(self):
        """Test that user_id_is_obj returns True for Users whose
        id matches the obj kwarg, and False for all other Users."""
        assert user_id_is_obj(self.provider, self.provider.id)
        assert not user_id_is_obj(self.admin, self.provider.id)
        assert not user_id_is_obj(self.patient, self.provider.id)
        assert not user_id_is_obj(self.anon, self.provider.id)
        assert not user_id_is_obj(self.provider, None)
        assert not user_id_is_obj(self.admin, None)
        assert not user_id_is_obj(self.patient, None)
        assert not user_id_is_obj(self.anon, None)
        assert not user_id_is_obj(self.provider, self.admin.id)
        assert not user_id_is_obj(self.admin, self.patient.id)
        assert not user_id_is_obj(self.patient, self.anon.id)
        assert not user_id_is_obj(self.anon, self.provider.id)
        assert not user_id_is_obj(self.provider, self.patient.id)
        assert not user_id_is_obj(self.admin, self.provider.id)
        assert not user_id_is_obj(self.patient, self.admin.id)
        assert not user_id_is_obj(self.anon, self.patient.id)

    def test__obj_without_creator(self):
        """Test that obj_without_creator returns True for Patients
        without a creator and False for Patients with a creator."""
        assert obj_without_creator(None, self.patient)
        assert obj_without_creator(None, self.provider_patient)
        assert obj_without_creator(None, self.provider)
        assert obj_without_creator(None, self.anon)

        delattr(self.patient, "creator")
        last_patient_history = self.patient.history.last()
        last_patient_history.history_user = self.patient
        last_patient_history.save()

        assert not obj_without_creator(None, self.patient)

    def test__user_is_obj_creator(self):
        """Test that user_is_obj_creator returns True for Users who are
        the creator of the object (Patient) and False for all other Users."""
        assert not user_is_obj_creator(self.provider, self.provider_patient)
        assert not user_is_obj_creator(self.admin, self.provider_patient)
        assert not user_is_obj_creator(self.patient, self.provider_patient)
        assert not user_is_obj_creator(self.anon, self.provider_patient)

        delattr(self.provider_patient, "creator")
        last_provider_patient_history = self.provider_patient.history.last()
        last_provider_patient_history.history_user = self.provider
        last_provider_patient_history.save()
        assert user_is_obj_creator(self.provider, self.provider_patient)
        assert not user_is_obj_creator(self.admin, self.provider_patient)
        assert not user_is_obj_creator(self.patient, self.provider_patient)
        assert not user_is_obj_creator(self.anon, self.provider_patient)

    def test__obj_is_patient_or_pseudopatient(self):
        """Test that obj_is_patient_or_pseudopatient returns True for Patients
        and False for all other Users."""
        assert obj_is_patient_or_pseudopatient(None, self.patient)
        assert obj_is_patient_or_pseudopatient(None, self.provider_patient)
        assert not obj_is_patient_or_pseudopatient(None, self.provider)
        assert not obj_is_patient_or_pseudopatient(None, self.admin)
        with pytest.raises(AttributeError):
            # AnonymousUser does not have a role attribute
            # so we expect an AttributeError to be raised
            assert obj_is_patient_or_pseudopatient(None, self.anon)
        assert obj_is_patient_or_pseudopatient(None, self.pseudopatient)

    def test__user_is_obj(self):
        """Test that user_is_obj returns True for Users and False for AnonymousUser."""
        assert user_is_obj(self.provider, self.provider)
        assert user_is_obj(self.admin, self.admin)
        assert user_is_obj(self.patient, self.patient)
        assert user_is_obj(self.anon, self.anon)
        assert not user_is_obj(self.provider, self.admin)
        assert not user_is_obj(self.admin, self.patient)
        assert not user_is_obj(self.patient, self.anon)
        assert not user_is_obj(self.anon, self.provider)

    def test__obj_without_provider(self):
        """Test that obj_without_provider returns True for Patients
        without a provider and False for Patients with a provider."""
        assert obj_without_provider(None, self.patient)
        assert not obj_without_provider(None, self.provider_patient)
        # Non-patient Users do not have a patientprofile attribute
        # so we expect an AttributeError to be raised
        with pytest.raises(AttributeError):
            assert obj_without_provider(None, self.provider)
        with pytest.raises(AttributeError):
            assert obj_without_provider(None, self.anon)

    def test__user_is_obj_provider(self):
        """Test that user_is_obj_provider returns True for Users who are
        Providers and False for all other Users."""
        assert user_is_obj_provider(self.provider, self.provider_patient)
        assert not user_is_obj_provider(self.admin, self.provider_patient)
        assert not user_is_obj_provider(self.patient, self.provider_patient)
        assert not user_is_obj_provider(self.anon, self.provider_patient)
        with pytest.raises(AttributeError):
            # Non-patient Users do not have a patientprofile attribute
            # so we expect an AttributeError to be raised
            assert user_is_obj_provider(self.provider, self.admin)

    def test__user_username_is_obj(self):
        """Test that user_username_is_obj returns True for Users whose
        username matches the obj kwarg, and False for all other Users."""
        assert user_username_is_obj(self.provider, self.provider.username)
        assert not user_username_is_obj(self.admin, self.provider.username)
        assert not user_username_is_obj(self.patient, self.provider.username)
        assert not user_username_is_obj(self.anon, self.provider.username)
        assert not user_username_is_obj(self.provider, None)
        assert not user_username_is_obj(self.admin, None)
        assert not user_username_is_obj(self.patient, None)
        assert not user_username_is_obj(self.anon, None)
        assert not user_username_is_obj(self.provider, self.admin.username)
        assert not user_username_is_obj(self.admin, self.patient.username)
        assert not user_username_is_obj(self.patient, self.anon.username)
        assert not user_username_is_obj(self.anon, self.provider.username)
        assert not user_username_is_obj(self.provider, self.patient.username)
        assert not user_username_is_obj(self.admin, self.provider.username)
        assert not user_username_is_obj(self.patient, self.admin.username)
        assert not user_username_is_obj(self.anon, self.patient.username)
        assert not user_username_is_obj(self.provider, self.provider)
        assert user_username_is_obj(self.admin, self.admin.username)
        assert user_username_is_obj(self.patient, self.patient.username)
        assert not user_username_is_obj(self.anon, self.anon.username)

    def test__user_is_a_provider(self):
        """Test that user_is_a_provider returns True for Users
        with the PROVIDER role and False for all other roles."""
        assert user_is_a_provider(self.provider)
        assert not user_is_a_provider(self.admin)
        assert not user_is_a_provider(self.patient)
        with pytest.raises(AttributeError):
            # AnonymousUser does not have a role attribute
            # so we expect an AttributeError to be raised
            assert user_is_a_provider(self.anon)

    def test__user_is_anonymous(self):
        """Test that user_is_anonymous returns True for AnonymousUser
        and False for all other Users."""
        assert user_is_anonymous(self.anon)
        assert not user_is_anonymous(self.provider)
        assert not user_is_anonymous(self.admin)
        assert not user_is_anonymous(self.patient)

    def test__user_is_admin(self):
        """Test that user_is_admin returns True for Users with the ADMIN role
        and False for all other roles."""
        assert user_is_admin(self.admin)
        assert not user_is_admin(self.provider)
        assert not user_is_admin(self.patient)
        with pytest.raises(AttributeError):
            user_is_admin(self.anon)

    def test__add_provider_patient(self):
        """Test that the add_provider_patient rule returns True for Users
        whose role is PROVIDER or ADMIN and when the provider kwarg is
        not None and either matches the request user's , who is a Provider,
        username, or when the request User is an Admin and the provider kwarg
        belongs to a Provider."""
        assert add_provider_patient(self.provider, self.provider.username)
        assert add_provider_patient(self.admin, self.provider.username)
        assert not add_provider_patient(self.patient, self.provider.username)
        assert not add_provider_patient(self.anon, self.provider.username)
        assert not add_provider_patient(self.provider, None)
        assert not add_provider_patient(self.provider, self.admin.username)
        assert not add_provider_patient(self.patient, self.patient.username)
        assert add_provider_patient(self.admin, self.admin.username)
        assert not add_provider_patient(self.anon, self.anon.username)

    def test__change_patient(self):
        """Test that change_patient returns True for Users Users who are an
        ADMIN, or who are the patient themselves, or who are the patient's
        provider, or for Patients without a provider."""
        assert change_patient(self.provider, self.patient)
        assert change_patient(self.admin, self.patient)
        assert change_patient(self.patient, self.patient)
        assert change_patient(self.anon, self.patient)
        with pytest.raises(AttributeError):
            assert not change_patient(self.provider, None)
        assert not change_patient(self.provider, self.admin)
        assert not change_patient(self.admin, self.provider)
        assert not change_patient(self.patient, self.provider)
        assert not change_patient(self.anon, self.provider)
        assert not change_patient(self.provider, self.provider)
        assert not change_patient(self.admin, self.admin)
        with pytest.raises(AttributeError):
            # AnonymousUser does not have a patientprofile attribute
            # so we expect an AttributeError to be raised
            change_patient(self.patient, self.anon)
        assert change_patient(self.anon, self.patient)
        assert not change_patient(self.anon, self.admin)
        assert not change_patient(self.anon, self.provider)

        # Set the patient's last history_user to the patient,
        # which makes them the creator. This should prevent other
        # non-admin Users from changing the patient.
        patients_last_history = self.patient.history.last()
        patients_last_history.history_user = self.patient
        patients_last_history.save()

        delattr(self.patient, "creator")

        assert not change_patient(self.provider, self.patient)
        assert change_patient(self.admin, self.patient)
        assert change_patient(self.patient, self.patient)
        assert not change_patient(self.anon, self.patient)

    def test__delete_patient(self):
        """Test that delete_patient returns True for Users who are the
        patient themselves, or who are the patient's provider."""
        assert delete_patient(self.provider, self.provider_patient)
        assert delete_patient(self.admin, self.provider_patient)
        assert delete_patient(self.patient, self.patient)
        assert not delete_patient(self.patient, self.provider_patient)
        assert not delete_patient(self.anon, self.provider_patient)
        with pytest.raises(AttributeError):
            assert not delete_patient(self.provider, None)
        assert not delete_patient(self.provider, self.admin)
        assert not delete_patient(self.admin, self.provider)
        assert not delete_patient(self.patient, self.provider)
        assert not delete_patient(self.anon, self.provider)
        assert not delete_patient(self.provider, self.provider)
        assert not delete_patient(self.admin, self.admin)
        with pytest.raises(AttributeError):
            # AnonymousUser does not have a patientprofile attribute
            # so we expect an AttributeError to be raised
            delete_patient(self.patient, self.anon)
        assert not delete_patient(self.anon, self.anon)
        assert not delete_patient(self.anon, self.patient)
        assert not delete_patient(self.anon, self.admin)
        assert not delete_patient(self.anon, self.provider)

        # Set the patient's last history_user to the patient,
        # which makes them the creator. This should prevent other
        # non-admin Users from deleting the patient.
        patients_last_history = self.patient.history.last()
        patients_last_history.history_user = self.patient
        patients_last_history.save()

        assert not delete_patient(self.provider, self.patient)
        assert delete_patient(self.admin, self.patient)
        assert delete_patient(self.patient, self.patient)
        assert not delete_patient(self.anon, self.patient)

    def test__view_patient(self):
        """Test that view_patient returns True for Users who are the
        patient themselves, or who are the patient's provider, or for
        Patients without a provider."""
        assert view_patient(self.provider, self.patient)
        assert view_patient(self.admin, self.patient)
        assert view_patient(self.patient, self.patient)
        assert view_patient(self.anon, self.patient)
        assert not view_patient(self.provider, self.admin)
        assert not view_patient(self.admin, self.provider)
        assert not view_patient(self.patient, self.provider)
        assert not view_patient(self.anon, self.provider)
        assert not view_patient(self.provider, self.provider)
        assert not view_patient(self.admin, self.admin)
        with pytest.raises(AttributeError):
            # AnonymousUser does not have a patientprofile attribute
            # so we expect an AttributeError to be raised
            assert not view_patient(self.patient, self.anon)
        assert view_patient(self.anon, self.patient)
        assert not view_patient(self.anon, self.admin)
        assert not view_patient(self.anon, self.provider)

        # Set the patient's last history_user to the patient,
        # which makes them the creator. This should prevent other
        # non-admin Users from viewing the patient.
        patients_last_history = self.patient.history.last()
        patients_last_history.history_user = self.patient
        patients_last_history.save()

        delattr(self.patient, "creator")

        assert not view_patient(self.provider, self.patient)
        assert view_patient(self.admin, self.patient)
        assert view_patient(self.patient, self.patient)
        assert not view_patient(self.anon, self.patient)


class TestUserPredicates(TestCase):
    def setUp(self):
        """Create a User with the Provider role."""
        self.provider = UserFactory()
        self.admin = UserFactory(role=Roles.ADMIN)
        self.patient = PatientFactory()
        self.anon = AnonymousUser()

    def test__change_user(self):
        """Test that change_user returns True for Users who are an
        ADMIN, or who are the user themselves."""
        assert change_user(self.provider, self.provider)
        assert change_user(self.admin, self.admin)
        assert change_user(self.patient, self.patient)
        assert change_user(self.admin, self.provider)
        assert not change_user(self.patient, self.provider)
        assert not change_user(self.anon, self.provider)
        assert not change_user(self.provider, self.admin)

        assert not change_user(self.patient, self.provider)
        assert not change_user(self.anon, self.provider)

    def test__delete_user(self):
        """Test that delete_user returns True for Users who are the
        user themselves."""
        assert delete_user(self.provider, self.provider)
        assert delete_user(self.admin, self.admin)
        assert delete_user(self.patient, self.patient)
        assert delete_user(self.admin, self.provider)
        assert not delete_user(self.patient, self.provider)
        assert not delete_user(self.anon, self.provider)
        assert not delete_user(self.provider, self.admin)
        assert not delete_user(self.patient, self.provider)
        assert not delete_user(self.anon, self.provider)

    def test__view_user(self):
        """Test that view_user returns True for Users who are the
        user themselves."""
        assert view_user(self.provider, self.provider)
        assert view_user(self.admin, self.admin)
        assert view_user(self.patient, self.patient)
        assert view_user(self.admin, self.provider)
        assert view_user(self.admin, self.patient)
        assert not view_user(self.patient, self.provider)
        assert not view_user(self.provider, self.anon)
        assert not view_user(self.provider, self.admin)
        assert not view_user(self.patient, self.provider)
        assert not view_user(self.anon, self.provider)
        assert not view_user(self.provider, self.patient)
        assert not view_user(self.patient, self.anon)
        assert not view_user(self.anon, self.anon)
        assert not view_user(self.anon, self.patient)
        assert not view_user(self.anon, self.admin)
        assert not view_user(self.anon, self.provider)
