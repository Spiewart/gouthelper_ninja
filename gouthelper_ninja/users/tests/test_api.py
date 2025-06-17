import json
from uuid import uuid4

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory
from gouthelper_ninja.utils.test_helpers import RESPONSE_FORBIDDEN
from gouthelper_ninja.utils.test_helpers import RESPONSE_NOT_FOUND
from gouthelper_ninja.utils.test_helpers import RESPONSE_SUCCESS
from gouthelper_ninja.utils.test_helpers import RESPONSE_UNAUTHORIZED
from gouthelper_ninja.utils.test_helpers import RESPONSE_UNPROCESSABLE_CONTENT


class TestCreatePatient(TestCase):
    def setUp(self):
        self.anon = AnonymousUser()
        self.provider = UserFactory()
        self.data = {
            "dateofbirth": {"dateofbirth": "2000-06-12"},
            "ethnicity": {"ethnicity": "Caucasian"},
            "gender": {"gender": 0},
        }

    def test__api(self):
        response = self.client.post(
            reverse("api-1.0.0:create_patient"),
            data=json.dumps(self.data),
            content_type="application/json",
        )

        assert response.status_code == RESPONSE_SUCCESS
        # Fetch patient by most recently created, will avoid problems
        # if fixtures are added later to create patients at test initialization.
        patient = Patient.objects.order_by("-created").first()
        assert isinstance(patient, Patient)
        assert str(patient.id) == response.json()["id"]
        assert patient.profile.provider is None
        assert patient.profile.provider_alias is None
        assert patient.dateofbirth.dateofbirth.strftime("%Y-%m-%d") == "2000-06-12"
        assert patient.ethnicity.ethnicity == "Caucasian"
        assert patient.gender.gender == 0

        self.client.force_login(self.provider)
        response = self.client.post(
            reverse("api-1.0.0:create_patient"),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        assert response.status_code == RESPONSE_SUCCESS
        patient = Patient.objects.order_by("-created").first()
        assert isinstance(patient, Patient)
        assert str(patient.id) == response.json()["id"]
        assert patient.profile.provider is None
        assert patient.profile.provider_alias is None
        assert patient.dateofbirth.dateofbirth.strftime("%Y-%m-%d") == "2000-06-12"
        assert patient.ethnicity.ethnicity == "Caucasian"
        assert patient.gender.gender == 0
        assert patient.creator == self.provider

    def test__data_with_provider_id(self):
        """Test that data with a provider_id will raise an error."""
        self.data["provider_id"] = str(self.provider.id)
        response = self.client.post(
            reverse("api-1.0.0:create_patient"),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        # The response should be a 422 for invalid input because extra parameters
        # are not allowed for PatientBaseSchema children.
        assert response.status_code == RESPONSE_UNPROCESSABLE_CONTENT
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "data", "provider_id"],
                    "msg": "Extra inputs are not permitted",
                    "type": "extra_forbidden",
                },
            ],
        }


class TestCreateProviderPatient(TestCase):
    def setUp(self):
        self.anon = AnonymousUser()
        self.provider = UserFactory()
        self.patient = PatientFactory()
        self.data = {
            "dateofbirth": {"dateofbirth": "2000-06-12"},
            "ethnicity": {"ethnicity": "Caucasian"},
            "gender": {"gender": 0},
        }

    def test__auth_required(self):
        response = self.client.post(
            reverse(
                "api-1.0.0:create_provider_patient",
                kwargs={"provider_id": self.provider.id},
            ),
            data=json.dumps(self.data),
            content_type="application/json",
        )

        assert response.status_code == RESPONSE_UNAUTHORIZED
        assert response.json() == {"detail": "Unauthorized"}

    def test__api(self):
        self.client.force_login(self.provider)
        response = self.client.post(
            reverse(
                "api-1.0.0:create_provider_patient",
                kwargs={"provider_id": self.provider.id},
            ),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        assert response.status_code == RESPONSE_SUCCESS
        patient = Patient.objects.get(id=response.json()["id"])
        assert patient.profile.provider == self.provider
        assert patient.profile.provider_alias is not None
        assert isinstance(patient.profile.provider_alias, int)
        assert patient.profile.provider_alias == 1

    def test__permissions(self):
        # A patient should not be able to create a patient for a provider
        self.client.force_login(self.patient)
        response = self.client.post(
            reverse(
                "api-1.0.0:create_provider_patient",
                kwargs={"provider_id": self.provider.id},
            ),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        assert response.status_code == RESPONSE_FORBIDDEN
        assert response.json() == {
            "detail": (
                f"{self.patient} does not have permission to create a "
                "patient for this provider."
            ),
        }
        # TODO: Test other roles, provider, creator combinations for permissions


class TestGetPatient(TestCase):
    def setUp(self):
        self.anon = AnonymousUser()
        self.patient = PatientFactory()
        self.provider = UserFactory()
        self.patient_with_provider = PatientFactory(provider=self.provider)
        self.url = reverse(
            "api-1.0.0:get_patient",
            kwargs={"patient_id": self.patient.id},
        )
        self.provider_patient_url = reverse(
            "api-1.0.0:get_patient",
            kwargs={"patient_id": self.patient_with_provider.id},
        )

    def test__auth(self):
        response = self.client.get(self.url)
        assert response.status_code == RESPONSE_SUCCESS

    def test__api(self):
        response = self.client.get(
            self.url,
        )

        assert response.status_code == RESPONSE_SUCCESS

        assert response.json()["id"] == str(self.patient.id)

    def test__404_not_found(self):
        fake_user_id = uuid4()
        response = self.client.get(
            f"/api/users/patients/{fake_user_id}",
            content_type="application/json",
        )
        assert response.status_code == RESPONSE_NOT_FOUND
        assert response.json() == {
            "detail": f"Patient with id: {fake_user_id} not found",
        }

    def test__permissions(self):
        response = self.client.get(
            self.provider_patient_url,
            {"patient_id": self.patient_with_provider.id},
        )
        assert response.status_code == RESPONSE_FORBIDDEN

        self.client.force_login(self.provider)
        response = self.client.get(
            self.provider_patient_url,
            data={"patient_id": self.patient_with_provider.id},
        )
        assert response.status_code == RESPONSE_SUCCESS
        assert response.json()["id"] == str(self.patient_with_provider.id)
        # TODO: Test other roles, provider, creator combinations for permissions


class TestGetPatients(TestCase):
    def setUp(self):
        self.anon = AnonymousUser()
        self.provider = UserFactory()
        self.patient = PatientFactory()
        self.admin = UserFactory(role=Roles.ADMIN)
        self.rf = RequestFactory()
        self.url = reverse("api-1.0.0:get_patients")

    def test__unauthenticated_user(self):
        response = self.client.get(
            self.url,
            user=self.anon,
        )
        assert response.status_code == RESPONSE_UNAUTHORIZED

    def test__authenticated_user(self):
        response = self.client.get(
            self.url,
            user=self.patient,
        )
        assert response.status_code == RESPONSE_UNAUTHORIZED

        self.client.force_login(self.provider)
        response = self.client.get(
            self.url,
            user=self.provider,
        )
        assert response.status_code == RESPONSE_SUCCESS
