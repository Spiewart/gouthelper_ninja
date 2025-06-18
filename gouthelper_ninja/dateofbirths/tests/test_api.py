from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from django.test import RequestFactory
from ninja.testing import TestClient

from gouthelper_ninja.dateofbirths.api import router
from gouthelper_ninja.dateofbirths.api import update_dateofbirth
from gouthelper_ninja.dateofbirths.models import DateOfBirth
from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.utils.test_helpers import RESPONSE_FORBIDDEN
from gouthelper_ninja.utils.test_helpers import RESPONSE_NOT_FOUND
from gouthelper_ninja.utils.test_helpers import RESPONSE_SUCCESS

if TYPE_CHECKING:
    from gouthelper_ninja.users.models import Patient
    from gouthelper_ninja.users.models import Provider

pytestmark = pytest.mark.django_db

factory = RequestFactory()
client = TestClient(router)


class TestUpdateDateOfBirth:
    def test__update_dateofbirth(self, patient: "Patient"):
        new_date = "1994-01-01"

        data = DateOfBirthEditSchema(dateofbirth=new_date)
        request = factory.post(
            f"/dateofbirths/update/{patient.dateofbirth.id}",
            data=data.dict(),
        )
        request.user = patient
        response = update_dateofbirth(
            request=request,
            dateofbirth_id=patient.dateofbirth.id,
            data=data,
        )

        assert isinstance(response, DateOfBirth)
        assert response.dateofbirth.strftime("%Y-%m-%d") == new_date
        # Verify that the dateofbirth was updated in the database
        updated_dob = DateOfBirth.objects.get(id=patient.dateofbirth.id)
        assert updated_dob.dateofbirth.strftime("%Y-%m-%d") == new_date

    def test__endpoint(self, patient: "Patient"):
        new_date = "1994-01-01"

        response = client.post(
            f"/dateofbirths/update/{patient.dateofbirth.id}",
            json={"dateofbirth": new_date},
        )

        assert response.status_code == RESPONSE_SUCCESS
        assert response.data["dateofbirth"] == new_date
        patient.dateofbirth.refresh_from_db()
        assert patient.dateofbirth.dateofbirth.strftime("%Y-%m-%d") == new_date

    def test__permissions(
        self,
        patient: "Patient",
        patient_with_provider: "Patient",
        provider: "Provider",
        another_provider: "Provider",
    ):
        """Test permissions for updating date of birth."""

        # Patient should be able to update their own date of birth
        response = client.post(
            f"/dateofbirths/update/{patient.dateofbirth.id}",
            json={"dateofbirth": "1994-01-01"},
        )
        assert response.status_code == RESPONSE_SUCCESS

        # AnonymousUser should not be able to update another patient's date of birth
        response = client.post(
            f"/dateofbirths/update/{patient_with_provider.dateofbirth.id}",
            json={"dateofbirth": "1994-01-01"},
        )
        assert response.status_code == RESPONSE_FORBIDDEN

        # Provider should be able to update his or her own patient's date of birth
        response = client.post(
            f"/dateofbirths/update/{patient_with_provider.dateofbirth.id}",
            json={"dateofbirth": "1994-01-01"},
            user=provider,
        )
        assert response.status_code == RESPONSE_SUCCESS

        # Another provider should not be able to update another patient's date of birth
        response = client.post(
            f"/dateofbirths/update/{patient_with_provider.dateofbirth.id}",
            json={"dateofbirth": "1994-01-01"},
            user=another_provider,
        )
        assert response.status_code == RESPONSE_FORBIDDEN

    def test__404(self):
        """Test that a 404 is returned when trying to
        update a non-existent date of birth."""
        fake_uuid = uuid4()
        response = client.post(
            f"/dateofbirths/update/{fake_uuid}",
            json={"dateofbirth": "1994-01-01"},
        )
        assert response.status_code == RESPONSE_NOT_FOUND
        assert response.data["detail"] == (
            f"DateOfBirth with id {fake_uuid} does not exist."
        )
