import pytest
from django.contrib.auth.hashers import check_password

from gouthelper_ninja.dateofbirths.models import DateOfBirth
from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.ethnicitys.models import Ethnicity
from gouthelper_ninja.ethnicitys.schema import EthnicityEditSchema
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.models import Gender
from gouthelper_ninja.genders.schema import GenderEditSchema
from gouthelper_ninja.medhistorys.schema import GoutEditSchema
from gouthelper_ninja.profiles.models import AdminProfile
from gouthelper_ninja.profiles.models import PatientProfile
from gouthelper_ninja.profiles.models import ProviderProfile
from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.models import Admin
from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.models import Provider
from gouthelper_ninja.users.models import User
from gouthelper_ninja.users.schema import PatientEditSchema
from gouthelper_ninja.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestAdminManager:
    def test_get_queryset(self):
        admin_user = UserFactory(role=Roles.ADMIN)
        UserFactory(role=Roles.PROVIDER)  # Non-admin user
        # Admin model uses AdminManager
        queryset = Admin.objects.all()
        assert queryset.count() == 1
        assert queryset.first() == admin_user
        assert admin_user.role == Roles.ADMIN

    def test_create_user(self):
        # To test AdminManager.create_user specifically:
        admin = Admin.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="securepassword",  # noqa: S106
            # ADMIN role set by Admin model manager
        )
        assert admin.username == "adminuser"
        assert admin.email == "admin@example.com"
        assert admin.check_password("securepassword")
        assert admin.role == Roles.ADMIN  # Set by Admin model's base_role
        # Check AdminProfile
        assert AdminProfile.objects.filter(user=admin).exists()
        profile = AdminProfile.objects.get(user=admin)
        assert profile is not None


class TestGoutHelperUserManager:
    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",  # noqa: S106
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert check_password("password123", user.password)
        assert not user.is_staff
        assert not user.is_superuser
        # Default role for User.objects.create_user() via GoutHelperUserManager
        # will be set by the model's save method if not explicitly passed,
        # which defaults to PROVIDER.
        assert user.role == Roles.PROVIDER

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            username="superadmin",
            email="admin@example.com",
            password="superpassword",  # noqa: S106
        )
        assert admin_user.username == "superadmin"
        assert admin_user.email == "admin@example.com"
        assert check_password("superpassword", admin_user.password)
        assert admin_user.is_staff
        assert admin_user.is_superuser
        assert admin_user.role == Roles.ADMIN
        # Assert that the AdminProfile is created for superusers
        assert AdminProfile.objects.filter(user=admin_user).exists()


class TestPatientManager:
    def test_get_queryset(self):
        patient_user = UserFactory(role=Roles.PSEUDOPATIENT)
        UserFactory(role=Roles.PROVIDER)  # Non-patient user

        # Patient model uses PatientManager
        queryset = Patient.objects.all()
        assert queryset.count() == 1
        assert queryset.first() == patient_user
        assert patient_user.role == Roles.PSEUDOPATIENT

    def test_create_patient_without_provider(self):
        dob_data = DateOfBirthEditSchema(dateofbirth="2000-01-01")
        ethnicity_data = EthnicityEditSchema(ethnicity=Ethnicitys.THAI)
        gender_data = GenderEditSchema(gender=Genders.FEMALE)
        gout_data = GoutEditSchema(
            history_of=False,
        )
        patient_data = PatientEditSchema(
            dateofbirth=dob_data,
            ethnicity=ethnicity_data,
            gender=gender_data,
            gout=gout_data,
        )

        patient = Patient.objects.gh_create(data=patient_data)

        assert patient.role == Roles.PSEUDOPATIENT
        assert patient.username is not None

        # Check PatientProfile
        assert PatientProfile.objects.filter(user=patient).exists()
        profile = PatientProfile.objects.get(user=patient)
        assert profile.provider is None
        assert profile.provider_alias is None

        # Check DateOfBirth
        assert DateOfBirth.objects.filter(patient=patient).exists()
        dob_obj = DateOfBirth.objects.get(patient=patient)
        assert dob_obj.dateofbirth.strftime("%Y-%m-%d") == "2000-01-01"

        # Check Ethnicity
        assert Ethnicity.objects.filter(patient=patient).exists()
        ethnicity_obj = Ethnicity.objects.get(patient=patient)
        assert ethnicity_obj.ethnicity == Ethnicitys.THAI

        # Check Gender
        assert Gender.objects.filter(patient=patient).exists()
        gender_obj = Gender.objects.get(patient=patient)
        assert gender_obj.gender == Genders.FEMALE

    def test_create_patient_with_provider(self):
        provider = UserFactory()  # Default role is PROVIDER

        dob_data = DateOfBirthEditSchema(dateofbirth="1995-05-15")
        ethnicity_data = EthnicityEditSchema(ethnicity=Ethnicitys.CAUCASIAN)
        gender_data = GenderEditSchema(gender=Genders.MALE)
        gout_data = GoutEditSchema(
            history_of=True,
        )
        patient_data = PatientEditSchema(
            dateofbirth=dob_data,
            ethnicity=ethnicity_data,
            gender=gender_data,
            gout=gout_data,
        )

        patient = Patient.objects.gh_create(data=patient_data, provider_id=provider.id)

        assert patient.role == Roles.PSEUDOPATIENT

        # Check PatientProfile
        assert PatientProfile.objects.filter(user=patient).exists()
        profile = PatientProfile.objects.get(user=patient)
        assert profile.provider == provider
        # Assuming this is the first patient for this provider
        assert profile.provider_alias == 1

        # Check DateOfBirth
        assert DateOfBirth.objects.filter(patient=patient).exists()
        dob_obj = DateOfBirth.objects.get(patient=patient)
        assert dob_obj.dateofbirth.strftime("%Y-%m-%d") == "1995-05-15"

        # Check Ethnicity
        assert Ethnicity.objects.filter(patient=patient).exists()
        ethnicity_obj = Ethnicity.objects.get(patient=patient)
        assert ethnicity_obj.ethnicity == Ethnicitys.CAUCASIAN

        # Check Gender
        assert Gender.objects.filter(patient=patient).exists()
        gender_obj = Gender.objects.get(patient=patient)
        assert gender_obj.gender == Genders.MALE

    def test_create_patient_with_provider_with_multiple_matching_patients(self):
        # This test ensures get_provider_alias is functional if not mocked
        provider = UserFactory()

        dob_data = DateOfBirthEditSchema(dateofbirth="1980-07-20")
        ethnicity_data = EthnicityEditSchema(ethnicity=Ethnicitys.AFRICANAMERICAN)
        gender_data = GenderEditSchema(gender=Genders.MALE)
        gout_data = GoutEditSchema(
            history_of=True,
        )
        patient_data = PatientEditSchema(
            dateofbirth=dob_data,
            ethnicity=ethnicity_data,
            gender=gender_data,
            gout=gout_data,
        )

        # Create another patient for the same provider to test alias increment
        Patient.objects.gh_create(data=patient_data, provider_id=provider.id)
        patient2 = Patient.objects.gh_create(data=patient_data, provider_id=provider.id)

        assert patient2.role == Roles.PSEUDOPATIENT
        profile2 = PatientProfile.objects.get(user=patient2)
        assert profile2.provider == provider
        assert profile2.provider_alias is not None
        expected_alias = 2
        assert profile2.provider_alias == expected_alias


class TestProviderManager:
    def test_get_queryset(self):
        provider_user = UserFactory(role=Roles.PROVIDER)
        UserFactory(role=Roles.PATIENT)  # Non-provider user

        # Provider model uses ProviderManager
        queryset = Provider.objects.all()
        assert queryset.count() == 1
        assert queryset.first() == provider_user
        assert provider_user.role == Roles.PROVIDER

    def test_create_user(self):
        # ProviderManager's create_user is intended to be called via
        # Provider.objects.create_user
        # which is inherited from BaseUserManager and then overridden
        # in ProviderManager.
        # The GoutHelperUserManager.create_user is the one typically
        # used for User.objects.create_user

        # To test ProviderManager.create_user specifically:
        provider = Provider.objects.create_user(
            username="providerdoc",
            email="provider@clinic.com",
            password="securepassword",  # noqa: S106
            # Default role is Provider
        )

        assert provider.username == "providerdoc"
        assert provider.email == "provider@clinic.com"
        assert provider.check_password("securepassword")
        assert provider.role == Roles.PROVIDER  # Set by Provider model's base_role

        # Check ProviderProfile
        assert ProviderProfile.objects.filter(user=provider).exists()
        profile = ProviderProfile.objects.get(user=provider)
        assert profile is not None
