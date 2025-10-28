from django.contrib.auth.hashers import check_password
from django.test import TestCase

from gouthelper_ninja.dateofbirths.models import DateOfBirth
from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.ethnicitys.models import Ethnicity
from gouthelper_ninja.ethnicitys.schema import EthnicityEditSchema
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.models import Gender
from gouthelper_ninja.genders.schema import GenderEditSchema
from gouthelper_ninja.goutdetails.schema import GoutDetailEditSchema
from gouthelper_ninja.medhistorys.schema import MedHistoryEditSchema
from gouthelper_ninja.profiles.models import AdminProfile
from gouthelper_ninja.profiles.models import PatientProfile
from gouthelper_ninja.profiles.models import ProviderProfile
from gouthelper_ninja.profiles.schema import PatientProfileEditSchema
from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.models import Admin
from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.models import Provider
from gouthelper_ninja.users.models import User
from gouthelper_ninja.users.schema import PatientEditSchema
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory


class TestAdminManager(TestCase):
    def setUp(self):
        # Create one admin and one non-admin provider user for queries
        self.admin_user = UserFactory(role=Roles.ADMIN)
        UserFactory(role=Roles.PROVIDER)

    def test_get_queryset(self):
        # Admin model uses AdminManager
        queryset = Admin.objects.all()
        assert queryset.count() == 1
        assert queryset.first() == self.admin_user
        assert self.admin_user.role == Roles.ADMIN

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
        assert AdminProfile.objects.filter(admin=admin).exists()
        profile = AdminProfile.objects.get(admin=admin)
        assert profile is not None


class TestGoutHelperUserManager(TestCase):
    def setUp(self):
        # no persistent fixtures required for these tests
        pass

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
        assert AdminProfile.objects.filter(admin=admin_user).exists()


class TestPatientManager(TestCase):
    def setUp(self):
        # provider used by several tests
        self.provider = UserFactory()
        self.dob_data = DateOfBirthEditSchema(
            dateofbirth="2000-01-01",
            patient={"id": None},
        )
        self.ethnicity_data = EthnicityEditSchema(
            ethnicity=Ethnicitys.THAI,
            patient={"id": None},
        )
        self.gender_data = GenderEditSchema(gender=Genders.FEMALE, patient={"id": None})
        self.gout_data = MedHistoryEditSchema(
            history_of=False,
            patient={"id": None},
        )
        self.goutdetail_data = GoutDetailEditSchema(
            at_goal=False,
            at_goal_long_term=False,
            flaring=False,
            on_ppx=False,
            on_ult=False,
            starting_ult=False,
            patient={"id": None},
        )
        self.patientprofile_data = PatientProfileEditSchema(
            id=None,
            patient={"id": None},
            provider=None,
        )
        self.patient_data = PatientEditSchema(
            id=None,
            dateofbirth=self.dob_data,
            ethnicity=self.ethnicity_data,
            gender=self.gender_data,
            gout=self.gout_data,
            goutdetail=self.goutdetail_data,
            patientprofile=self.patientprofile_data,
        )

    def test_get_queryset(self):
        patient_user = UserFactory(role=Roles.PSEUDOPATIENT)
        UserFactory(role=Roles.PROVIDER)  # Non-patient user

        # Patient model uses PatientManager
        queryset = Patient.objects.all()
        assert queryset.count() == 1
        assert queryset.first() == patient_user
        assert patient_user.role == Roles.PSEUDOPATIENT

    def test_create_patient_without_provider(self):
        patient = Patient.objects.gh_create(data=self.patient_data)

        assert patient.role == Roles.PSEUDOPATIENT
        assert patient.username is not None

        # Check PatientProfile
        assert PatientProfile.objects.filter(patient=patient).exists()
        profile = PatientProfile.objects.get(patient=patient)
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
        self.patientprofile_data.provider = {"id": self.provider.id}
        self.patient_data.patientprofile = self.patientprofile_data

        patient = Patient.objects.gh_create(data=self.patient_data)

        assert patient.role == Roles.PSEUDOPATIENT

        # Check PatientProfile
        assert PatientProfile.objects.filter(patient=patient).exists()
        profile = PatientProfile.objects.get(patient=patient)
        assert profile.provider == self.provider

        # Check DateOfBirth
        assert DateOfBirth.objects.filter(patient=patient).exists()
        dob_obj = DateOfBirth.objects.get(patient=patient)
        assert dob_obj.dateofbirth == self.dob_data.dateofbirth

        # Check Ethnicity
        assert Ethnicity.objects.filter(patient=patient).exists()
        ethnicity_obj = Ethnicity.objects.get(patient=patient)
        assert ethnicity_obj.ethnicity == self.ethnicity_data.ethnicity

        # Check Gender
        assert Gender.objects.filter(patient=patient).exists()
        gender_obj = Gender.objects.get(patient=patient)
        assert gender_obj.gender == self.gender_data.gender

    def test_create_patient_with_provider_with_multiple_matching_patients(self):
        # Create another patient for the same provider to test alias increment
        Patient.objects.gh_create(data=self.patient_data)
        assert Patient.objects.gh_create(data=self.patient_data)

    def test_update_patient(self):
        # Create initial patient
        patient = PatientFactory()

        # Copy the patient's data to reference later in the test
        original_gout = patient.gout.history_of
        original_goutdetail_at_goal = patient.goutdetail.at_goal
        original_goutdetail_at_goal_long_term = patient.goutdetail.at_goal_long_term
        original_goutdetail_flaring = patient.goutdetail.flaring
        original_goutdetail_on_ppx = patient.goutdetail.on_ppx
        original_goutdetail_on_ult = patient.goutdetail.on_ult
        original_goutdetail_starting_ult = patient.goutdetail.starting_ult

        assert patient.patientprofile.provider is None

        # Prepare updated data
        self.dob_data.patient.id = patient.id
        self.ethnicity_data.patient.id = patient.id
        self.gender_data.patient.id = patient.id
        self.gout_data.patient.id = patient.id
        self.goutdetail_data.patient.id = patient.id
        self.patientprofile_data.patient.id = patient.id
        self.patientprofile_data.provider = {"id": self.provider.id}
        self.patient_data.id = patient.id
        self.patient_data.dateofbirth = self.dob_data
        self.patient_data.ethnicity = self.ethnicity_data
        self.patient_data.gender = self.gender_data
        self.patient_data.patientprofile = self.patientprofile_data

        patient = Patient.objects.gh_update(
            instance=patient,
            data=self.patient_data,
        )

        assert patient.dateofbirth.dateofbirth == self.dob_data.dateofbirth
        assert patient.ethnicity.ethnicity == self.ethnicity_data.ethnicity
        assert patient.gender.gender == self.gender_data.gender
        assert patient.patientprofile.provider == self.provider

        # Assert that the fields not part of the PatientEditSchema remain unchanged
        assert patient.gout.history_of == original_gout
        assert patient.goutdetail.at_goal == original_goutdetail_at_goal
        assert (
            patient.goutdetail.at_goal_long_term
            == original_goutdetail_at_goal_long_term
        )
        assert patient.goutdetail.flaring == original_goutdetail_flaring
        assert patient.goutdetail.on_ppx == original_goutdetail_on_ppx
        assert patient.goutdetail.on_ult == original_goutdetail_on_ult
        assert patient.goutdetail.starting_ult == original_goutdetail_starting_ult


class TestProviderManager(TestCase):
    def setUp(self):
        self.provider_user = UserFactory(role=Roles.PROVIDER)
        UserFactory(role=Roles.PSEUDOPATIENT)

    def test_get_queryset(self):
        # Provider model uses ProviderManager
        queryset = Provider.objects.all()
        assert queryset.count() == 1
        assert queryset.first() == self.provider_user
        assert self.provider_user.role == Roles.PROVIDER

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
        assert ProviderProfile.objects.filter(provider=provider).exists()
        profile = ProviderProfile.objects.get(provider=provider)
        assert profile is not None
