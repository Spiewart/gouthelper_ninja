import json
from http import HTTPStatus
from uuid import uuid4

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory


class TestCreatePatient(TestCase):
    def setUp(self):
        self.anon = AnonymousUser()
        self.provider = UserFactory()
        self.data = {
            "dateofbirth": {"dateofbirth": "2000-06-12"},
            "ethnicity": {"ethnicity": "Caucasian"},
            "gender": {"gender": 0},
            MHTypes.GOUT.name.lower(): {"history_of": True},
            "goutdetail": {
                "at_goal": True,
                "at_goal_long_term": True,
                "flaring": False,
                "on_ppx": True,
                "on_ult": False,
                "starting_ult": True,
            },
        }

    def test__api(self):
        response = self.client.post(
            reverse("api-1.0.0:create_patient"),
            data=json.dumps(self.data),
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.OK
        # Fetch patient by most recently created, will avoid problems
        # if fixtures are added later to create patients at test initialization.
        patient = Patient.objects.order_by("-created").first()
        assert isinstance(patient, Patient)
        assert str(patient.id) == response.json()["id"]
        assert patient.patientprofile.provider is None
        assert patient.patientprofile.provider_alias is None
        assert patient.dateofbirth.dateofbirth.strftime("%Y-%m-%d") == "2000-06-12"
        assert patient.ethnicity.ethnicity == "Caucasian"
        assert patient.gender.gender == 0

        self.client.force_login(self.provider)
        response = self.client.post(
            reverse("api-1.0.0:create_patient"),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.OK
        patient = Patient.objects.order_by("-created").first()
        assert isinstance(patient, Patient)
        assert str(patient.id) == response.json()["id"]
        assert patient.patientprofile.provider is None
        assert patient.patientprofile.provider_alias is None
        assert patient.dateofbirth.dateofbirth.strftime("%Y-%m-%d") == "2000-06-12"
        assert patient.ethnicity.ethnicity == "Caucasian"
        assert patient.gender.gender == 0
        assert patient.creator == self.provider


class TestCreateProviderPatient(TestCase):
    def setUp(self):
        self.anon = AnonymousUser()
        self.provider = UserFactory()
        self.patient = PatientFactory()
        self.data = {
            "dateofbirth": {"dateofbirth": "2000-06-12"},
            "ethnicity": {"ethnicity": "Caucasian"},
            "gender": {"gender": 0},
            MHTypes.GOUT.name.lower(): {"history_of": True},
            "goutdetail": {
                "at_goal": True,
                "at_goal_long_term": True,
                "flaring": False,
                "on_ppx": True,
                "on_ult": False,
                "starting_ult": True,
            },
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

        assert response.status_code == HTTPStatus.UNAUTHORIZED
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
        assert response.status_code == HTTPStatus.OK
        patient = Patient.objects.get(id=response.json()["id"])
        assert patient.patientprofile.provider == self.provider
        assert patient.patientprofile.provider_alias is not None
        assert isinstance(patient.patientprofile.provider_alias, int)
        assert patient.patientprofile.provider_alias == 1

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
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {
            "detail": (
                f"{self.patient} does not have permission to create a "
                "patient for this provider."
            ),
        }

        # An admin should be able to create a patient for any provider
        admin_user = UserFactory(role=Roles.ADMIN)
        self.client.force_login(admin_user)
        response = self.client.post(
            reverse(
                "api-1.0.0:create_provider_patient",
                kwargs={"provider_id": self.provider.id},
            ),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.OK
        patient = Patient.objects.get(id=response.json()["id"])
        assert patient.patientprofile.provider == self.provider
        # The creator should be the admin user who made the request
        assert patient.creator == admin_user

        # A provider should not be able to create a patient for another provider
        other_provider = UserFactory(role=Roles.PROVIDER)
        self.client.force_login(other_provider)
        response = self.client.post(
            reverse(
                "api-1.0.0:create_provider_patient",
                kwargs={"provider_id": self.provider.id},
            ),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {
            "detail": (
                f"{other_provider} does not have permission to create a "
                "patient for this provider."
            ),
        }

    def test__invalid_provider_id(self):
        self.client.force_login(self.provider)
        invalid_provider_id = uuid4()
        response = self.client.post(
            reverse(
                "api-1.0.0:create_provider_patient",
                kwargs={"provider_id": invalid_provider_id},
            ),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {
            "detail": f"Provider with id: {invalid_provider_id} not found.",
        }


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
        assert response.status_code == HTTPStatus.OK

    def test__api(self):
        response = self.client.get(
            self.url,
        )

        assert response.status_code == HTTPStatus.OK

        assert response.json()["id"] == str(self.patient.id)

    def test__404_not_found(self):
        fake_user_id = uuid4()
        response = self.client.get(
            f"/api/users/patients/{fake_user_id}",
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {
            "detail": f"Patient with id: {fake_user_id} not found",
        }

    def test__permissions(self):
        # Anonymous user trying to access a patient with a provider
        response = self.client.get(
            self.provider_patient_url,
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {
            "detail": "AnonymousUser does not have permission to view this patient.",
        }

        # Anonymous user trying to access a patient without a provider (should succeed)
        response = self.client.get(self.url)
        assert response.status_code == HTTPStatus.OK
        assert response.json()["id"] == str(self.patient.id)

        # Patient trying to access their own details (patient has no provider)
        self.client.force_login(self.patient)
        response = self.client.get(self.url)
        assert response.status_code == HTTPStatus.OK
        assert response.json()["id"] == str(self.patient.id)

        # Patient trying to access another patient's details
        # (other patient has a provider)
        other_patient_with_provider = PatientFactory(provider=UserFactory())
        other_patient_url = reverse(
            "api-1.0.0:get_patient",
            kwargs={"patient_id": other_patient_with_provider.id},
        )
        response = self.client.get(other_patient_url)
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {
            "detail": f"{self.patient} does not have permission to view this patient.",
        }

        # Provider trying to access their own patient
        self.client.force_login(self.provider)
        response = self.client.get(self.provider_patient_url)
        assert response.status_code == HTTPStatus.OK
        assert response.json()["id"] == str(self.patient_with_provider.id)

        # Provider trying to access a patient not assigned to them
        # (but without a provider)
        response = self.client.get(self.url)
        assert response.status_code == HTTPStatus.OK
        assert response.json()["id"] == str(self.patient.id)

        # Admin user trying to access any patient
        admin_user = UserFactory(role=Roles.ADMIN)
        self.client.force_login(admin_user)
        response = self.client.get(self.url)
        assert response.status_code == HTTPStatus.OK
        assert response.json()["id"] == str(self.patient.id)

        response = self.client.get(self.provider_patient_url)
        assert response.status_code == HTTPStatus.OK
        assert response.json()["id"] == str(self.patient_with_provider.id)

        # Test user who created a patient (but is not their provider)
        creator_user = UserFactory(role=Roles.PROVIDER)
        created_patient = PatientFactory()
        history = created_patient.history.first()
        history.history_user = creator_user
        history.save()
        self.client.force_login(creator_user)
        created_patient_url = reverse(
            "api-1.0.0:get_patient",
            kwargs={"patient_id": created_patient.id},
        )
        response = self.client.get(created_patient_url)
        assert response.status_code == HTTPStatus.OK
        assert response.json()["id"] == str(created_patient.id)

        self.client.force_login(self.provider)
        response = self.client.get(
            self.provider_patient_url,
            data={"patient_id": self.patient_with_provider.id},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["id"] == str(self.patient_with_provider.id)


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
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test__authenticated_user(self):
        response = self.client.get(
            self.url,
            user=self.patient,
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

        self.client.force_login(self.provider)
        response = self.client.get(
            self.url,
            user=self.provider,
        )
        assert response.status_code == HTTPStatus.OK


class TestUpdatePatient(TestCase):
    def setUp(self):
        self.anon = AnonymousUser()
        self.provider = UserFactory()
        self.patient = PatientFactory()
        self.patient_with_provider = PatientFactory(provider=self.provider)
        self.patient_with_creator = PatientFactory(creator=self.provider)

        self.url = reverse(
            "api-1.0.0:update_patient",
            kwargs={"patient_id": self.patient.id},
        )
        self.data = {
            "dateofbirth": {"dateofbirth": "2000-06-12"},
            "ethnicity": {"ethnicity": Ethnicitys.KOREAN},
            "gender": {"gender": Genders.MALE},
            MHTypes.GOUT.name.lower(): {"history_of": True},
            "goutdetail": {
                "at_goal": True,
                "at_goal_long_term": True,
                "flaring": False,
                "on_ppx": True,
                "on_ult": False,
                "starting_ult": True,
            },
        }

    def test__patient_without_provider(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.data),
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.OK
        patient = Patient.objects.get(id=self.patient.id)
        assert patient.ethnicity.ethnicity == Ethnicitys.KOREAN
        assert patient.gender.gender == Genders.MALE
        assert patient.dateofbirth.dateofbirth.strftime("%Y-%m-%d") == "2000-06-12"
        assert patient.gout.history_of is True
        assert patient.goutdetail.at_goal is True
        assert patient.goutdetail.at_goal_long_term is True
        assert patient.goutdetail.flaring is False
        assert patient.goutdetail.on_ppx is True
        assert patient.goutdetail.on_ult is False
        assert patient.goutdetail.starting_ult is True

    def test__patient_with_provider(self):
        response = self.client.post(
            reverse(
                "api-1.0.0:update_patient",
                kwargs={"patient_id": self.patient_with_provider.id},
            ),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        self.client.force_login(self.patient)
        response = self.client.post(
            reverse(
                "api-1.0.0:update_patient",
                kwargs={"patient_id": self.patient_with_provider.id},
            ),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        self.client.force_login(self.provider)
        response = self.client.post(
            reverse(
                "api-1.0.0:update_patient",
                kwargs={"patient_id": self.patient_with_provider.id},
            ),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.OK
        patient = Patient.objects.get(id=self.patient_with_provider.id)
        assert patient.ethnicity.ethnicity == Ethnicitys.KOREAN
        assert patient.gender.gender == Genders.MALE

    def test__patient_with_creator(self):
        response = self.client.post(
            reverse(
                "api-1.0.0:update_patient",
                kwargs={"patient_id": self.patient_with_creator.id},
            ),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        self.client.force_login(self.patient)
        response = self.client.post(
            reverse(
                "api-1.0.0:update_patient",
                kwargs={"patient_id": self.patient_with_creator.id},
            ),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        self.client.force_login(self.provider)
        response = self.client.post(
            reverse(
                "api-1.0.0:update_patient",
                kwargs={"patient_id": self.patient_with_creator.id},
            ),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.OK
        patient = Patient.objects.get(id=self.patient_with_creator.id)
        assert patient.ethnicity.ethnicity == Ethnicitys.KOREAN
        assert patient.gender.gender == Genders.MALE
        assert patient.dateofbirth.dateofbirth.strftime("%Y-%m-%d") == "2000-06-12"
        assert patient.gout.history_of is True
        assert patient.goutdetail.at_goal is True
        assert patient.goutdetail.at_goal_long_term is True
        assert patient.goutdetail.flaring is False
        assert patient.goutdetail.on_ppx is True
        assert patient.goutdetail.on_ult is False
        assert patient.goutdetail.starting_ult is True
