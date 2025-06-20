import json
from uuid import uuid4

import pytest
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from gouthelper_ninja.dateofbirths.api import update_dateofbirth
from gouthelper_ninja.dateofbirths.models import DateOfBirth
from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory
from gouthelper_ninja.utils.test_helpers import RESPONSE_FORBIDDEN
from gouthelper_ninja.utils.test_helpers import RESPONSE_NOT_FOUND
from gouthelper_ninja.utils.test_helpers import RESPONSE_SUCCESS

pytestmark = pytest.mark.django_db


class TestUpdateDateOfBirth(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.patient = PatientFactory()
        self.provider = UserFactory()
        self.patient_with_provider = PatientFactory(provider=self.provider)
        self.another_provider = UserFactory()
        self.new_dob = {"dateofbirth": "1994-01-01"}

    def test__update_dateofbirth(self):
        request = self.factory.post(
            f"/dateofbirths/update/{self.patient.dateofbirth.id}",
            data=DateOfBirthEditSchema(**self.new_dob),
            content_type="application/json",
        )
        request.user = self.patient
        response = update_dateofbirth(
            request=request,
            dateofbirth_id=self.patient.dateofbirth.id,
            data=DateOfBirthEditSchema(**self.new_dob),
        )

        assert isinstance(response, DateOfBirth)
        assert response.dateofbirth.strftime("%Y-%m-%d") == self.new_dob["dateofbirth"]
        # Verify that the dateofbirth was updated in the database
        updated_dob = DateOfBirth.objects.get(id=self.patient.dateofbirth.id)
        assert (
            updated_dob.dateofbirth.strftime("%Y-%m-%d") == self.new_dob["dateofbirth"]
        )

    def test__endpoint(self):
        response = self.client.post(
            reverse(
                "api-1.0.0:update_dateofbirth",
                kwargs={"dateofbirth_id": self.patient.dateofbirth.id},
            ),
            data=json.dumps(self.new_dob),
            content_type="application/json",
        )

        assert response.status_code == RESPONSE_SUCCESS
        assert response.json()["dateofbirth"] == self.new_dob["dateofbirth"]
        self.patient.dateofbirth.refresh_from_db()
        assert (
            self.patient.dateofbirth.dateofbirth.strftime("%Y-%m-%d")
            == self.new_dob["dateofbirth"]
        )

    def test__permissions(
        self,
    ):
        """Test permissions for updating date of birth."""

        # Patient should be able to update their own date of birth
        response = self.client.post(
            reverse(
                "api-1.0.0:update_dateofbirth",
                kwargs={"dateofbirth_id": self.patient.dateofbirth.id},
            ),
            data=json.dumps(self.new_dob),
            content_type="application/json",
        )
        assert response.status_code == RESPONSE_SUCCESS

        # AnonymousUser should not be able to update another
        # self.patient's date of birth
        response = self.client.post(
            reverse(
                "api-1.0.0:update_dateofbirth",
                kwargs={"dateofbirth_id": self.patient_with_provider.dateofbirth.id},
            ),
            data=json.dumps(self.new_dob),
            content_type="application/json",
        )
        assert response.status_code == RESPONSE_FORBIDDEN

        # Provider should be able to update his or her own self.patient's date of birth
        self.client.force_login(self.provider)
        response = self.client.post(
            reverse(
                "api-1.0.0:update_dateofbirth",
                kwargs={"dateofbirth_id": self.patient_with_provider.dateofbirth.id},
            ),
            data=json.dumps(self.new_dob),
            content_type="application/json",
        )
        assert response.status_code == RESPONSE_SUCCESS

        # Another provider should not be able to update
        # another self.patient's date of birth
        self.client.force_login(self.another_provider)
        response = self.client.post(
            reverse(
                "api-1.0.0:update_dateofbirth",
                kwargs={"dateofbirth_id": self.patient_with_provider.dateofbirth.id},
            ),
            data=json.dumps(self.new_dob),
            content_type="application/json",
        )
        assert response.status_code == RESPONSE_FORBIDDEN

    def test__404(self):
        """Test that a 404 is returned when trying to
        update a non-existent date of birth."""
        fake_uuid = uuid4()
        response = self.client.post(
            f"/api/dateofbirths/update/{fake_uuid}",
            data=json.dumps(self.new_dob),
            content_type="application/json",
        )
        assert response.status_code == RESPONSE_NOT_FOUND
        assert response.json()["detail"] == (
            f"DateOfBirth with id {fake_uuid} does not exist."
        )
