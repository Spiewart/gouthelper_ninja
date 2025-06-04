from uuid import UUID
from uuid import uuid4

from django.apps import apps
from django.contrib.auth.base_user import BaseUserManager

from gouthelper_ninja.profiles.helpers import get_provider_alias
from gouthelper_ninja.profiles.models import PatientProfile
from gouthelper_ninja.profiles.models import ProviderProfile
from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.utils.helpers import age_calc


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

    def create(self, **kwargs):
        kwargs.update(
            {
                "role": Roles.PSEUDOPATIENT,
            },
        )

        if "username" not in kwargs:
            kwargs["username"] = uuid4().hex[:30]

        dateofbirth = kwargs.pop("dateofbirth")
        ethnicity = kwargs.pop("ethnicity")
        gender = kwargs.pop("gender")
        provider_id = kwargs.pop("provider", None)

        patient = super().create(**kwargs)

        profile_kwargs = {
            "provider_id": provider_id,
            "user": patient,
            "provider_alias": get_provider_alias(
                provider=provider_id,
                age=age_calc(dateofbirth),
                gender=gender,
            )
            if provider_id
            else None,
        }

        if profile_kwargs["provider_id"] is not None:
            # TODO: implement setting of provider_alias with method
            if isinstance(profile_kwargs["provider_id"], UUID):
                profile_kwargs["provider_alias"] = 1
            else:
                profile_kwargs["provider_alias"] = 1

        PatientProfile.objects.create(
            **profile_kwargs,
        )

        # Create related models
        apps.get_model("dateofbirths.DateOfBirth").objects.create(
            patient=patient,
            dateofbirth=dateofbirth,
        )
        apps.get_model("ethnicitys.Ethnicity").objects.create(
            patient=patient,
            ethnicity=ethnicity,
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
