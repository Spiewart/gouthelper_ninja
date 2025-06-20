import json
from typing import TYPE_CHECKING
from uuid import UUID
from uuid import uuid4

import pytest
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from ninja.errors import AuthorizationError

from gouthelper_ninja.genders.api import update_gender
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.models import Gender
from gouthelper_ninja.genders.schema import GenderEditSchema
from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory
from gouthelper_ninja.utils.test_helpers import RESPONSE_FORBIDDEN
from gouthelper_ninja.utils.test_helpers import RESPONSE_NOT_FOUND
from gouthelper_ninja.utils.test_helpers import RESPONSE_SUCCESS

if TYPE_CHECKING:
    from gouthelper_ninja.users.models import User

pytestmark = pytest.mark.django_db


class TestUpdateGender(TestCase):
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

        # Determine a new gender value different from the default factory value
        original_gender = self.patient.gender.gender
        if original_gender == Genders.MALE.value:
            self.new_gender_value = Genders.FEMALE.value
        else:
            self.new_gender_value = Genders.MALE.value

        self.new_gender_data = {"gender": self.new_gender_value}
        self.payload_schema = GenderEditSchema(**self.new_gender_data)

    def test__update_gender(self):
        # Test the core function logic directly
        gender_obj = self.patient.gender
        original_gender = gender_obj.gender

        # Ensure the new value is different for the update to trigger save
        if self.new_gender_value == original_gender:
            self.new_gender_value = (
                Genders.FEMALE.value
                if original_gender == Genders.MALE.value
                else Genders.MALE.value
            )
            self.new_gender_data = {"gender": self.new_gender_value}
            self.payload_schema = GenderEditSchema(**self.new_gender_data)

        request = self.factory.post(
            # URL path doesn't strictly matter for direct call
            f"/genders/update/{gender_obj.id}",
            data=self.payload_schema.dict(),
            content_type="application/json",
        )
        request.user = self.patient  # Mock the user as the patient themselves

        response_gender = update_gender(
            request=request,
            gender_id=gender_obj.id,
            data=self.payload_schema,
        )

        assert isinstance(response_gender, Gender)
        assert response_gender.gender == self.new_gender_value

        # Verify that the gender was updated in the database
        updated_gender_db = Gender.objects.get(id=gender_obj.id)
        assert updated_gender_db.gender == self.new_gender_value

    def test__endpoint(self):
        # Test the API endpoint using the Django test client
        gender_obj = self.patient.gender
        url = reverse("api-1.0.0:update_gender", kwargs={"gender_id": gender_obj.id})

        # Log in a user who has permission (e.g., the patient themselves)
        self.client.force_login(self.patient)

        response = self.client.post(
            url,
            data=json.dumps(self.new_gender_data),
            content_type="application/json",
        )

        assert response.status_code == RESPONSE_SUCCESS
        assert response.json()["gender"] == self.new_gender_value
        gender_obj.refresh_from_db()
        assert gender_obj.gender == self.new_gender_value

    def test__permissions(self):
        """Test permissions for updating gender."""
        gender_no_affiliations = self.patient.gender
        gender_with_provider = self.patient_with_provider.gender
        gender_with_creator = self.patient_with_creator.gender

        def _make_request_and_call_update(
            user: "User",
            target_gender_id: UUID,
            data_schema: GenderEditSchema,
        ):
            request = self.factory.post(
                f"/genders/update/{target_gender_id}",
                data=data_schema.dict(),
            )
            request.user = user
            return update_gender(
                request=request,
                gender_id=target_gender_id,
                data=data_schema,
            )

        # Admin can update any patient's Gender
        updated_gender_admin = _make_request_and_call_update(
            self.admin_user,
            gender_with_provider.id,
            self.payload_schema,
        )
        assert isinstance(updated_gender_admin, Gender)

        # Patient can update their own Gender
        updated_gender_self = _make_request_and_call_update(
            self.patient,
            gender_no_affiliations.id,
            self.payload_schema,
        )
        assert isinstance(updated_gender_self, Gender)

        # Patient's provider can update patient's Gender
        updated_gender_by_provider = _make_request_and_call_update(
            self.provider,
            gender_with_provider.id,
            self.payload_schema,
        )
        assert isinstance(updated_gender_by_provider, Gender)

        # Patient's creator can update patient's Gender
        updated_gender_by_creator = _make_request_and_call_update(
            self.provider,
            gender_with_creator.id,
            self.payload_schema,
        )
        assert isinstance(updated_gender_by_creator, Gender)

        # Unrelated provider cannot update patient's
        # Gender (when patient has affiliations)
        with pytest.raises(AuthorizationError) as excinfo_unrelated_provider:
            _make_request_and_call_update(
                self.another_provider,
                gender_with_provider.id,
                self.payload_schema,
            )
        assert excinfo_unrelated_provider.value.status_code == RESPONSE_FORBIDDEN

        # Patient cannot update another (unrelated) patient's Gender
        with pytest.raises(AuthorizationError) as excinfo_unrelated_patient:
            _make_request_and_call_update(
                self.patient,
                gender_with_provider.id,
                self.payload_schema,
            )
        assert excinfo_unrelated_patient.value.status_code == RESPONSE_FORBIDDEN

        # Anonymous user cannot update any Gender (unless patient has no affiliations)
        with pytest.raises(AuthorizationError) as excinfo_anon:
            _make_request_and_call_update(
                UserFactory(is_active=False),
                gender_with_provider.id,
                self.payload_schema,
            )
        assert excinfo_anon.value.status_code == RESPONSE_FORBIDDEN

        # Authenticated (but unrelated) user CAN update Gender if the target patient
        # has NO affiliations
        patient_no_affiliations_fresh = PatientFactory()
        gender_no_affiliations_fresh = patient_no_affiliations_fresh.gender
        updated_gender_auth_no_affiliations = _make_request_and_call_update(
            self.another_provider,
            gender_no_affiliations_fresh.id,
            self.payload_schema,
        )
        assert isinstance(updated_gender_auth_no_affiliations, Gender)

    def test__404(self):
        """Test that a 404 is returned when trying to update a non-existent gender."""
        fake_uuid = uuid4()
        url = reverse("api-1.0.0:update_gender", kwargs={"gender_id": fake_uuid})

        self.client.force_login(self.admin_user)
        response = self.client.post(
            url,
            data=json.dumps(self.new_gender_data),
            content_type="application/json",
        )
        assert response.status_code == RESPONSE_NOT_FOUND
        assert (
            response.json()["detail"] == f"Gender with id {fake_uuid} does not exist."
        )
