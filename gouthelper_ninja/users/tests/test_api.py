from datetime import timedelta

from django.db.models import QuerySet
from django.test import TestCase

from gouthelper_ninja.dateofbirths.models import DateOfBirth
from gouthelper_ninja.ethnicitys.models import Ethnicity
from gouthelper_ninja.genders.models import Gender
from gouthelper_ninja.profiles.models import PatientProfile
from gouthelper_ninja.users.api import create_patient
from gouthelper_ninja.users.api import get_patient
from gouthelper_ninja.users.api import get_patients
from gouthelper_ninja.users.api import update_patient
from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.models import User
from gouthelper_ninja.users.schema import PatientCreateSchema
from gouthelper_ninja.users.schema import PatientUpdateSchema
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory


class TestAPI(TestCase):
    def setUp(self):
        self.users = [UserFactory(role=Roles.PSEUDOPATIENT) for _ in range(3)]
        self.provider = UserFactory()  # Default role is PROVIDER
        self.request = None
        self.patient_create_schema = PatientCreateSchema(
            provider=None,
            dateofbirth="2000-01-01",
            ethnicity="Caucasian",
            gender=0,
        )

    def test__get_patients(self):
        response = get_patients(self.request)

        num_patients = 3
        assert isinstance(response, QuerySet)
        assert len(response) == num_patients
        assert all(isinstance(user, User) for user in response)

    def test__get_patient(self):
        response = get_patient(self.request, patient_id=self.users[0].id)

        assert isinstance(response, User)
        assert response.id == self.users[0].id

    def test__create_patient(self):
        response = create_patient(data=self.patient_create_schema, request=self.request)

        assert isinstance(response, User)
        assert response.role == Roles.PSEUDOPATIENT

        assert response.profile is not None
        assert isinstance(response.profile, PatientProfile)
        assert response.profile.provider is None
        assert response.profile.provider_alias is None

        assert response.dateofbirth
        assert isinstance(response.dateofbirth, DateOfBirth)
        assert response.dateofbirth.dateofbirth.strftime("%Y-%m-%d") == "2000-01-01"

        assert response.ethnicity
        assert isinstance(response.ethnicity, Ethnicity)
        assert response.ethnicity.ethnicity == "Caucasian"

        assert response.gender
        assert isinstance(response.gender, Gender)
        assert response.gender.get_gender_display() == "Male"

    def test__create_patient_with_provider(self):
        self.patient_create_schema.provider = self.provider.id
        response = create_patient(
            data=self.patient_create_schema,
            request=self.request,
        )
        assert isinstance(response, User)
        assert response.role == Roles.PSEUDOPATIENT

        assert response.profile is not None
        assert isinstance(response.profile, PatientProfile)
        assert response.profile.provider is not None
        assert response.profile.provider == self.provider
        assert response.profile.provider_alias is not None
        assert isinstance(response.profile.provider_alias, int)
        assert response.profile.provider_alias == 1

        assert response.dateofbirth
        assert isinstance(response.dateofbirth, DateOfBirth)
        assert response.dateofbirth.dateofbirth.strftime("%Y-%m-%d") == "2000-01-01"

        assert response.ethnicity
        assert isinstance(response.ethnicity, Ethnicity)
        assert response.ethnicity.ethnicity == "Caucasian"

        assert response.gender
        assert isinstance(response.gender, Gender)
        assert response.gender.get_gender_display() == "Male"

    def test__update_patient(self):
        patient = PatientFactory()

        updated_dob = patient.dateofbirth.dateofbirth + timedelta(days=90)

        data = PatientUpdateSchema(
            dateofbirth=updated_dob,
            ethnicity=patient.ethnicity.ethnicity,
            gender=patient.gender.gender,
        )

        assert patient.dateofbirth.dateofbirth != updated_dob

        response = update_patient(
            request=self.request,
            patient_id=patient.id,
            data=data,
        )

        assert isinstance(response, User)
        assert response.id == patient.id
        assert response.dateofbirth.dateofbirth == updated_dob
