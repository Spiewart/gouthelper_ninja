from typing import TYPE_CHECKING

import pytest
from django.contrib.auth.models import AnonymousUser

from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.rules import delete_object
from gouthelper_ninja.rules import view_object
from gouthelper_ninja.users.tests.factories import PatientFactory

if TYPE_CHECKING:
    from gouthelper_ninja.users.models import Admin
    from gouthelper_ninja.users.models import Patient
    from gouthelper_ninja.users.models import Provider


pytestmark = pytest.mark.django_db


class MockGenericObject:
    """
    A mock object to simulate the 'obj' parameter in the rule predicates.
    The predicates expect obj.patient to be the patient User instance.
    """

    def __init__(self, patient_user_instance=None):
        self.patient = patient_user_instance


class TestAddObject:
    """Tests the add_object rule. The object will typically be a Patient returned by a
    View or API endpoint, so the request user will have to be the patient, an admin,
    the patient's provider, or the patient's creator."""

    def test__anyone_can_add_for_anonymous_user(
        self,
        anon: "AnonymousUser",
        patient: "Patient",
        provider: "Provider",
        admin: "Admin",
    ):
        # An anonymous user can add a patient, as long as the patient
        # does not have a provider or creator
        assert add_object(anon, patient)
        assert add_object(provider, patient)
        assert add_object(admin, patient)

    def test__admin_can_add(self, admin: "Admin", patient: "Patient"):
        assert add_object(admin, patient)

    def test__user_is_patient_can_add(self, patient: "Patient"):
        # The user adding is the patient themselves
        assert add_object(patient, patient)

    def test__user_is_patients_provider_can_add(
        self,
        provider: "Provider",
        patient_with_provider: "Patient",
    ):
        # The user adding is the provider of the patient
        assert add_object(provider, patient_with_provider)

    def test__user_is_patients_creator_can_add(
        self,
        provider: "Provider",
        patient_with_creator: "Patient",
    ):
        # The user adding is the creator of the patient
        assert add_object(provider, patient_with_creator)

    def test__permission_denied_for_unrelated_user(
        self,
        another_provider: "Provider",
        patient_with_provider: "Patient",
    ):
        # The user adding is not related to the patient
        assert not add_object(another_provider, patient_with_provider)


class TestChangeObject:
    def test__user_is_admin_can_change(self, admin: "Admin", patient: "Patient"):
        obj = MockGenericObject(patient_user_instance=patient)
        assert change_object(admin, obj)

    def test__user_is_obj_patient_can_change(self, patient: "Patient"):
        # The user changing is the patient associated with the object
        obj = MockGenericObject(patient_user_instance=patient)
        assert change_object(patient, obj)

    def test__user_is_obj_patients_provider_can_change(
        self,
        provider: "Provider",
        patient_with_provider: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_provider)
        assert change_object(provider, obj)

    def test__user_is_obj_patients_creator_can_change(
        self,
        provider: "Provider",
        patient_with_creator: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_creator)
        assert change_object(provider, obj)

    def test__obj_patient_without_provider_and_creator_can_be_changed_by_any_user(
        self,
        provider: "Provider",
        patient: "Patient",
        anon: "AnonymousUser",
        another_provider: "Provider",
    ):
        obj = MockGenericObject(patient_user_instance=patient)
        # Any non-related user should be able to change
        assert change_object(provider, obj)
        assert change_object(anon, obj)
        assert change_object(another_provider, obj)

    def test__denied_for_unrelated_user_when_patient_has_affiliations(
        self,
        provider: "Provider",
        another_provider: "Provider",
        patient_with_provider: "Patient",
        patient_with_creator: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_provider)
        assert not change_object(another_provider, obj)
        assert not change_object(
            patient_with_creator,
            obj,
        )  # patient_with_creator (user) is unrelated to patient_with_provider (in obj)
        assert change_object(
            provider,
            obj,
        )  # provider can change their own patient's data

        obj = MockGenericObject(patient_user_instance=patient_with_creator)
        assert not change_object(another_provider, obj)
        assert not change_object(
            patient_with_provider,
            obj,
        )  # patient_with_provider (user) is unrelated to patient_with_creator (in obj)
        assert change_object(provider, obj)  # provider (creator) can change

    def test__denied_if_not_admin_and_not_related(
        self,
        patient_with_provider: "Patient",
        another_provider: "Provider",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_provider)
        assert not change_object(another_provider, obj)

    def test__denied_for_unrelated_provider_with_patient_with_different_provider(
        self,
        provider: "Provider",
        another_provider: "Provider",
    ):
        patient_obj_instance = PatientFactory(provider=another_provider)
        obj = MockGenericObject(patient_user_instance=patient_obj_instance)
        assert not change_object(provider, obj)

    def test__denied_for_unrelated_provider_with_patient_with_different_creator(
        self,
        patient_with_creator: "Patient",
        another_provider: "Provider",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_creator)
        assert not change_object(another_provider, obj)

    def test__denied_for_anonymous_user_for_patient_with_creator(
        self,
        patient_with_creator: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_creator)
        assert not change_object(AnonymousUser(), obj)

    def test__denied_for_anonymous_user_for_patient_with_provider(
        self,
        patient_with_provider: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_provider)
        assert not change_object(AnonymousUser(), obj)


class TestDeleteObject:
    def test__admin_can_delete(self, admin: "Admin", patient: "Patient"):
        obj = MockGenericObject(patient_user_instance=patient)
        assert delete_object(admin, obj)

    def test__user_is_obj_patient_can_delete(self, patient: "Patient"):
        # The user deleting is the patient associated with the object
        obj = MockGenericObject(patient_user_instance=patient)
        assert delete_object(patient, obj)

    def test__user_is_obj_patients_provider_can_delete(
        self,
        provider: "Provider",
        patient_with_provider: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_provider)
        assert delete_object(provider, obj)

    def test__user_is_obj_patients_creator_can_delete(
        self,
        provider: "Provider",
        patient_with_creator: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_creator)
        assert delete_object(provider, obj)

    def test__anonymous_user_cannot_delete(
        self,
        anon: "AnonymousUser",
        patient: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient)
        assert not delete_object(anon, obj)

    def test__denied_for_unrelated_user_when_patient_has_provider(
        self,
        another_provider: "Provider",
        patient_with_provider: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_provider)
        assert not delete_object(another_provider, obj)

    def test__denied_for_unrelated_user_when_patient_has_creator(
        self,
        another_provider: "Provider",
        patient_with_creator: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_creator)
        assert not delete_object(another_provider, obj)

    def test__denied_for_unrelated_user_when_patient_has_no_affiliations(
        self,
        another_provider: "Provider",
        patient: "Patient",
    ):
        # Even if patient has no provider/creator, unrelated user
        # (not admin, not patient) cannot delete
        obj = MockGenericObject(patient_user_instance=patient)
        assert not delete_object(another_provider, obj)

    def test__patient_cannot_delete_other_patient_object(
        self,
        patient: "Patient",
        patient_with_provider: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_provider)
        assert not delete_object(patient, obj)


class TestViewObject:
    def test__user_is_admin_can_view(self, admin: "Admin", patient: "Patient"):
        obj = MockGenericObject(patient_user_instance=patient)
        assert view_object(admin, obj)

    def test__user_is_obj_patient_can_view(self, patient: "Patient"):
        # The user viewing is the patient associated with the object
        obj = MockGenericObject(patient_user_instance=patient)
        assert view_object(patient, obj)

    def test__user_is_obj_patients_provider_can_view(
        self,
        provider: "Provider",
        patient_with_provider: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_provider)

        assert view_object(provider, obj)

    def test__user_is_obj_patients_creator_can_view(
        self,
        provider: "Provider",
        patient_with_creator: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_creator)
        assert view_object(provider, obj)

    def test__obj_patient_without_provider_and_creator_can_be_viewed_by_any_user(
        self,
        provider: "Provider",
        patient: "Patient",
        anon: "AnonymousUser",
        another_provider: "Provider",
    ):
        obj = MockGenericObject(patient_user_instance=patient)
        # Any non-related user should be able to view
        assert view_object(provider, obj)
        assert view_object(anon, obj)
        assert view_object(another_provider, obj)

    def test__denied_for_unrelated_user_when_patient_has_affiliations(
        self,
        provider: "Provider",
        another_provider: "Provider",
        patient_with_provider: "Patient",
        patient_with_creator: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_provider)
        assert not view_object(another_provider, obj)
        assert not view_object(patient_with_creator, obj)
        assert view_object(provider, obj)  # provider can view their own patient's data

        obj = MockGenericObject(patient_user_instance=patient_with_creator)
        assert not view_object(another_provider, obj)
        assert not view_object(patient_with_provider, obj)
        assert view_object(provider, obj)

    def test__denied_if_not_admin_and_not_related(
        self,
        patient_with_provider: "Patient",
        another_provider: "Provider",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_provider)

        assert not view_object(another_provider, obj)

    def test__denied_for_unrelated_provider_with_patient_with_different_provider(
        self,
        provider: "Provider",
        another_provider: "Provider",
    ):
        # Patient has a provider, but no creator (implicitly None)
        patient_obj_instance = PatientFactory(provider=another_provider)

        obj = MockGenericObject(patient_user_instance=patient_obj_instance)
        # The (obj_patient_without_provider & obj_patient_without_creator) condition
        # fails provider is not otherwise related.
        assert not view_object(provider, obj)

    def test__denied_for_unrelated_provider_with_patient_with_different_creator(
        self,
        patient_with_creator: "Patient",
        another_provider: "Provider",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_creator)

        assert not view_object(another_provider, obj)

    def test__denied_for_anonymous_user_for_patient_with_creator(
        self,
        patient_with_creator: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_creator)

        # Anonymous user should not be able to view the object
        assert not view_object(AnonymousUser(), obj)

    def test__denied_for_anonymous_user_for_patient_with_provider(
        self,
        patient_with_provider: "Patient",
    ):
        obj = MockGenericObject(patient_user_instance=patient_with_provider)

        # Anonymous user should not be able to view the object
        assert not view_object(AnonymousUser(), obj)
