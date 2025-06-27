import json
from http import HTTPStatus
from typing import TYPE_CHECKING
from uuid import UUID
from uuid import uuid4

import pytest
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from ninja.errors import AuthorizationError

from gouthelper_ninja.ethnicitys.api import update_ethnicity
from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.ethnicitys.models import Ethnicity
from gouthelper_ninja.ethnicitys.schema import EthnicityEditSchema
from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from gouthelper_ninja.users.models import User

pytestmark = pytest.mark.django_db


class TestUpdateEthnicity(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Patient without provider/creator
        self.patient = PatientFactory()
        # Patient with provider (self.provider)
        self.provider = UserFactory()
        self.patient_with_provider = PatientFactory(provider=self.provider)
        # Patient with creator (self.provider)
        self.patient_with_creator = PatientFactory(creator=self.provider)
        self.another_provider = UserFactory()
        self.admin_user = UserFactory(role=Roles.ADMIN)

        # Determine a new ethnicity value different from the default factory value
        original_ethnicity = self.patient.ethnicity.ethnicity
        if original_ethnicity == Ethnicitys.CAUCASIAN.value:
            self.new_ethnicity_value = Ethnicitys.AFRICANAMERICAN.value
        else:
            self.new_ethnicity_value = Ethnicitys.CAUCASIAN.value

        self.new_ethnicity_data = {"ethnicity": self.new_ethnicity_value}
        self.payload_schema = EthnicityEditSchema(**self.new_ethnicity_data)

    def test__update_ethnicity(self):
        # Test the core function logic directly
        ethnicity_obj = self.patient.ethnicity
        original_ethnicity = ethnicity_obj.ethnicity

        # Ensure the new value is different for the update to trigger save
        if self.new_ethnicity_value == original_ethnicity:
            self.new_ethnicity_value = Ethnicitys.THAI.value
            self.new_ethnicity_data = {"ethnicity": self.new_ethnicity_value}
            self.payload_schema = EthnicityEditSchema(**self.new_ethnicity_data)

        request = self.factory.post(
            # URL path doesn't strictly matter for direct call
            f"/ethnicitys/update/{ethnicity_obj.id}",
            data=self.payload_schema.dict(),
            content_type="application/json",
        )
        request.user = self.patient  # Mock the user as the patient themselves

        response_ethnicity = update_ethnicity(
            request=request,
            ethnicity_id=ethnicity_obj.id,
            data=self.payload_schema,
        )

        assert isinstance(response_ethnicity, Ethnicity)
        assert response_ethnicity.ethnicity == self.new_ethnicity_value

        # Verify that the ethnicity was updated in the database
        updated_ethnicity_db = Ethnicity.objects.get(id=ethnicity_obj.id)
        assert updated_ethnicity_db.ethnicity == self.new_ethnicity_value

    def test__endpoint(self):
        # Test the API endpoint using the Django test client
        ethnicity_obj = self.patient.ethnicity
        url = reverse(
            "api-1.0.0:update_ethnicity",
            kwargs={"ethnicity_id": ethnicity_obj.id},
        )

        # Log in a user who has permission (e.g., the patient themselves)
        self.client.force_login(self.patient)

        response = self.client.post(
            url,
            data=json.dumps(self.new_ethnicity_data),
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json()["ethnicity"] == self.new_ethnicity_value
        ethnicity_obj.refresh_from_db()
        assert ethnicity_obj.ethnicity == self.new_ethnicity_value

    def test__permissions(self):
        """Test permissions for updating ethnicity."""
        ethnicity_no_affiliations = self.patient.ethnicity
        ethnicity_with_provider = self.patient_with_provider.ethnicity
        ethnicity_with_creator = self.patient_with_creator.ethnicity

        def _make_request_and_call_update(
            user: "User",
            target_ethnicity_id: UUID,
            data_schema: EthnicityEditSchema,
        ):
            request = self.factory.post(
                f"/ethnicitys/update/{target_ethnicity_id}",
                data=data_schema.dict(),
            )
            request.user = user
            return update_ethnicity(
                request=request,
                ethnicity_id=target_ethnicity_id,
                data=data_schema,
            )

        # Admin can update any patient's Ethnicity
        updated_ethnicity_admin = _make_request_and_call_update(
            self.admin_user,
            ethnicity_with_provider.id,
            self.payload_schema,
        )
        assert isinstance(updated_ethnicity_admin, Ethnicity)

        # Patient can update their own Ethnicity
        updated_ethnicity_self = _make_request_and_call_update(
            self.patient,
            ethnicity_no_affiliations.id,
            self.payload_schema,
        )
        assert isinstance(updated_ethnicity_self, Ethnicity)

        # Patient's provider can update patient's Ethnicity
        updated_ethnicity_by_provider = _make_request_and_call_update(
            self.provider,
            ethnicity_with_provider.id,
            self.payload_schema,
        )
        assert isinstance(updated_ethnicity_by_provider, Ethnicity)

        # Patient's creator can update patient's Ethnicity
        updated_ethnicity_by_creator = _make_request_and_call_update(
            self.provider,
            ethnicity_with_creator.id,
            self.payload_schema,  # provider is also creator
        )
        assert isinstance(updated_ethnicity_by_creator, Ethnicity)

        # Unrelated provider cannot update patient's
        # Ethnicity (when patient has affiliations)
        with pytest.raises(AuthorizationError) as excinfo_unrelated_provider:
            _make_request_and_call_update(
                self.another_provider,
                ethnicity_with_provider.id,
                self.payload_schema,
            )
        assert excinfo_unrelated_provider.value.status_code == HTTPStatus.FORBIDDEN

        # Patient cannot update another (unrelated) patient's Ethnicity
        with pytest.raises(AuthorizationError) as excinfo_unrelated_patient:
            _make_request_and_call_update(
                self.patient,
                ethnicity_with_provider.id,
                self.payload_schema,
            )
        assert excinfo_unrelated_patient.value.status_code == HTTPStatus.FORBIDDEN

        # Anonymous user cannot update any Ethnicity
        # (unless patient has no affiliations, which is covered by the rule test)
        with pytest.raises(AuthorizationError) as excinfo_anon:
            _make_request_and_call_update(
                UserFactory(is_active=False),
                ethnicity_with_provider.id,
                # Use AnonymousUser for permission checks
                self.payload_schema,
            )
        assert excinfo_anon.value.status_code == HTTPStatus.FORBIDDEN

        # Authenticated (but unrelated) user CAN update Ethnicity
        # if the target patient has NO affiliations (provider/creator).
        # This is a key part of the `change_object` rule.
        # Use a fresh patient with no affiliations to ensure this test is isolated.
        patient_no_affiliations_fresh = PatientFactory()
        ethnicity_no_affiliations_fresh = patient_no_affiliations_fresh.ethnicity
        updated_ethnicity_auth_no_affiliations = _make_request_and_call_update(
            self.another_provider,
            ethnicity_no_affiliations_fresh.id,
            self.payload_schema,
        )
        assert isinstance(updated_ethnicity_auth_no_affiliations, Ethnicity)

    def test__404(self):
        """Test that a 404 is returned when trying to
        update a non-existent ethnicity."""
        fake_uuid = uuid4()
        url = reverse(
            "api-1.0.0:update_ethnicity",
            kwargs={"ethnicity_id": fake_uuid},
        )

        # Log in a user who would normally have permission if the object existed
        self.client.force_login(self.admin_user)

        response = self.client.post(
            url,
            data=json.dumps(self.new_ethnicity_data),
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json()["detail"] == (
            f"Ethnicity with id {fake_uuid} does not exist."
        )
