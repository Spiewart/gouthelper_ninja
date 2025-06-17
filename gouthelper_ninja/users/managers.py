from typing import TYPE_CHECKING
from typing import Union
from uuid import uuid4

from django.apps import apps
from django.contrib.auth.base_user import BaseUserManager

from gouthelper_ninja.profiles.helpers import get_provider_alias
from gouthelper_ninja.profiles.models import PatientProfile
from gouthelper_ninja.profiles.models import ProviderProfile
from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.schema import PatientEditSchema
from gouthelper_ninja.utils.helpers import age_calc

if TYPE_CHECKING:
    from uuid import UUID


class AdminManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=Roles.ADMIN)


class GoutHelperUserManager(BaseUserManager):
    """Custom User model manager for GoutHelper.
    It only overrides the create_superuser method."""

    def create_user(self, username, email, password=None):
        """Create and save a User with the given email and password."""
        user = self.model(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password. Set
        role to ADMIN."""
        user = self.model(
            email=email,
            is_staff=True,
            is_superuser=True,
            role=Roles.ADMIN,
            **extra_fields,
        )
        user.set_password(password)
        user.save()
        return user


class PatientManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=Roles.PSEUDOPATIENT)

    def create(self, data: PatientEditSchema, provider_id: Union["UUID", None] = None):
        dateofbirth = data.dateofbirth.dateofbirth
        gender = data.gender.gender

        patient = super().create(
            role=Roles.PSEUDOPATIENT,
            username=uuid4().hex[:30],
        )

        PatientProfile.objects.create(
            provider_id=provider_id,
            user=patient,
            provider_alias=get_provider_alias(
                provider_id=provider_id,
                age=age_calc(dateofbirth),
                gender=gender,
            )
            if provider_id
            else None,
        )

        # Create related models
        apps.get_model("dateofbirths.DateOfBirth").objects.create(
            patient=patient,
            dateofbirth=dateofbirth,
        )
        apps.get_model("ethnicitys.Ethnicity").objects.create(
            patient=patient,
            ethnicity=data.ethnicity.ethnicity,
        )
        apps.get_model("genders.Gender").objects.create(
            patient=patient,
            gender=gender,
        )
        return patient


class ProviderManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=Roles.PROVIDER)

    def create_user(self, **kwargs):
        """Create a provider user."""
        user = super().create(**kwargs)
        ProviderProfile.objects.create(user=user)
        return user
