from decimal import Decimal
from http import HTTPStatus

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from gouthelper_ninja.ckddetails.choices import DialysisChoices
from gouthelper_ninja.ckddetails.choices import DialysisDurations
from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory


class TestCreateCkdDetail(TestCase):
    def setUp(self):
        self.provider = UserFactory()
        self.patient = PatientFactory()
        self.provider_patient = PatientFactory(provider=self.provider)
        self.data = {
            "dialysis": False,
            "dialysis_duration": None,
            "dialysis_type": None,
            "stage": Stages.THREE,
            "age": 45,
            "gender": Genders.MALE,
            "creatinine": Decimal("1.9"),
        }

    def test__successful_create(self):
        response = self.client.post(
            f"/api/ckddetails/create/{self.patient.id}",
            data=self.data,
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.OK
        assert str(self.patient.id) == response.json()["patient_id"]
        assert self.patient.ckddetail
        assert self.patient.ckddetail.stage == Stages.THREE
        assert self.patient.ckddetail.dialysis is False
        assert self.patient.ckddetail.dialysis_duration is None
        assert self.patient.ckddetail.dialysis_type is None
        # Assert that the json keys match the newly created CkdDetail
        assert set(response.json().keys()) == {
            "id",
            "patient_id",
            "stage",
            "dialysis",
            "dialysis_duration",
            "dialysis_type",
        }
        # Assert that the values match the data provided
        assert response.json()["stage"] == Stages.THREE.value
        assert response.json()["dialysis"] is False
        assert response.json()["dialysis_duration"] is None
        assert response.json()["dialysis_type"] is None

    def test__404_if_patient_does_not_exist(self):
        response = self.client.post(
            "/api/ckddetails/create/00000000-0000-0000-0000-000000000000",
            data=self.data,
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {
            "detail": (
                "Patient with id 00000000-0000-0000-0000-000000000000 does not exist."
            ),
        }

    def test__403_if_user_does_not_have_permission(self):
        response = self.client.post(
            f"/api/ckddetails/create/{self.provider_patient.id}",
            data=self.data,
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {
            "detail": (
                f"{AnonymousUser()} does not have permission to create a "
                "CkdDetail for this patient."
            ),
        }

        self.client.force_login(self.patient)
        response = self.client.post(
            f"/api/ckddetails/create/{self.provider_patient.id}",
            data=self.data,
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {
            "detail": (
                f"{self.patient} does not have permission to create a "
                "CkdDetail for this patient."
            ),
        }

        self.client.force_login(self.provider)
        response = self.client.post(
            f"/api/ckddetails/create/{self.provider_patient.id}",
            data=self.data,
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.OK


class TestCkdDetailUpdate(TestCase):
    def setUp(self):
        self.patient = PatientFactory(
            ckddetail={"stage": Stages.THREE},
        )
        self.provider = UserFactory()
        self.provider_patient = PatientFactory(
            provider=self.provider,
            ckddetail={"stage": Stages.FOUR},
        )
        self.data = {
            "dialysis": True,
            "dialysis_duration": DialysisDurations.LESSTHANSIX,
            "dialysis_type": DialysisChoices.PERITONEAL,
        }

    def test__successful_update(self):
        response = self.client.post(
            f"/api/ckddetails/update/{self.patient.ckddetail.id}",
            data=self.data,
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.OK
        assert str(self.patient.id) == response.json()["patient_id"]
        self.patient.ckddetail.refresh_from_db()
        assert self.patient.ckddetail
        assert self.patient.ckddetail.stage == Stages.FIVE
        assert self.patient.ckddetail.dialysis is True
        assert self.patient.ckddetail.dialysis_duration == DialysisDurations.LESSTHANSIX
        assert self.patient.ckddetail.dialysis_type == DialysisChoices.PERITONEAL

    def test__404_if_ckddetail_does_not_exist(self):
        response = self.client.post(
            "/api/ckddetails/update/00000000-0000-0000-0000-000000000000",
            data=self.data,
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {
            "detail": (
                "CkdDetail with id 00000000-0000-0000-0000-000000000000 does not exist."
            ),
        }

    def test__403_if_user_does_not_have_permission(self):
        response = self.client.post(
            f"/api/ckddetails/update/{self.provider_patient.ckddetail.id}",
            data=self.data,
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {
            "detail": (
                f"{AnonymousUser()} does not have permission to update this CkdDetail."
            ),
        }

        self.client.force_login(self.patient)
        response = self.client.post(
            f"/api/ckddetails/update/{self.provider_patient.ckddetail.id}",
            data=self.data,
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {
            "detail": (
                f"{self.patient} does not have permission to update this CkdDetail."
            ),
        }

        self.client.force_login(self.provider)
        response = self.client.post(
            f"/api/ckddetails/update/{self.provider_patient.ckddetail.id}",
            data=self.data,
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.OK
