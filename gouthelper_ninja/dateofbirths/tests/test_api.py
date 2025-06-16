from django.test import TestCase
from ninja.testing import TestClient

from gouthelper_ninja.dateofbirths.api import router
from gouthelper_ninja.dateofbirths.api import update_dateofbirth
from gouthelper_ninja.dateofbirths.models import DateOfBirth
from gouthelper_ninja.dateofbirths.schema import DateOfBirthNestedSchema
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.utils.test_helpers import RESPONSE_SUCCESS


class TestAPI(TestCase):
    def setUp(self):
        self.patient = PatientFactory()
        self.dateofbirth = self.patient.dateofbirth

    def test__update_dateofbirth(self):
        new_date = "1994-01-01"

        data = DateOfBirthNestedSchema(dateofbirth=new_date)
        response = update_dateofbirth(
            request=None,  # In a real test, you would mock the request
            dateofbirth_id=self.dateofbirth.id,
            data=data,
        )

        assert isinstance(response, DateOfBirth)
        assert response.dateofbirth.strftime("%Y-%m-%d") == new_date
        # Verify that the dateofbirth was updated in the database
        updated_dob = DateOfBirth.objects.get(id=self.dateofbirth.id)
        assert updated_dob.dateofbirth.strftime("%Y-%m-%d") == new_date

    def test__update_dateofbirth_api_endpoint(self):
        client = TestClient(router)
        new_date = "1994-01-01"

        response = client.post(
            f"/dateofbirths/update/{self.dateofbirth.id}",
            json={"dateofbirth": new_date},
        )

        assert response.status_code == RESPONSE_SUCCESS
        assert response.data["dateofbirth"] == new_date
        self.dateofbirth.refresh_from_db()
        assert self.dateofbirth.dateofbirth.strftime("%Y-%m-%d") == new_date
