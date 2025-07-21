from typing import TYPE_CHECKING
from typing import Union
from uuid import uuid4

from django.apps import apps
from django.contrib.auth.base_user import BaseUserManager

from gouthelper_ninja.profiles.helpers import get_provider_alias
from gouthelper_ninja.profiles.models import AdminProfile
from gouthelper_ninja.profiles.models import PatientProfile
from gouthelper_ninja.profiles.models import ProviderProfile
from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.schema import PatientEditSchema
from gouthelper_ninja.utils.helpers import age_calc

if TYPE_CHECKING:
    from uuid import UUID


class GoutHelperUserManager(BaseUserManager):
    """Custom User model manager for GoutHelper.
    It only overrides the create_superuser method."""

    def create_user(self, username, email, password, role=Roles.PROVIDER):
        """Create and save a User with the given email and password."""
        user = self.model(
            username=username,
            email=email,
            role=role,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, role=Roles.ADMIN, **extra_fields):
        """Create and save a SuperUser with the given email and password. Set
        role to ADMIN."""
        user = self.model(
            email=email,
            is_staff=True,
            is_superuser=True,
            role=role,
            **extra_fields,
        )
        user.set_password(password)
        user.save()
        AdminProfile.objects.create(user=user)
        return user


class AdminManager(GoutHelperUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=Roles.ADMIN)

    def create_user(self, username, email, password, role=Roles.ADMIN):
        """Create a provider user."""
        user = super().create_user(
            username=username,
            email=email,
            password=password,
            role=role,
        )
        AdminProfile.objects.create(user=user)
        return user


class PatientManager(GoutHelperUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=Roles.PSEUDOPATIENT)

    def gh_create(
        self,
        data: PatientEditSchema,
        provider_id: Union["UUID", None] = None,
    ):
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
        apps.get_model("medhistorys.Gout").objects.create(
            patient=patient,
            history_of=data.gout.history_of,
        )
        apps.get_model("goutdetails.GoutDetail").objects.create(
            patient=patient,
            at_goal=data.goutdetail.at_goal,
            at_goal_long_term=data.goutdetail.at_goal_long_term,
            flaring=data.goutdetail.flaring,
            on_ppx=data.goutdetail.on_ppx,
            on_ult=data.goutdetail.on_ult,
            starting_ult=data.goutdetail.starting_ult,
        )
        menopause = data.menopause
        if menopause:
            apps.get_model("medhistorys.Menopause").objects.create(
                patient=patient,
                history_of=menopause.history_of,
            )
        return patient

    def create_user(self, username, email, password, role=Roles.PSEUDOPATIENT):
        """Create a provider user."""
        user = super().create_user(
            username=username,
            email=email,
            password=password,
            role=role,
        )
        PatientProfile.objects.create(user=user)
        return user


class ProviderManager(GoutHelperUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=Roles.PROVIDER)

    def create_user(self, username, email, password, role=Roles.PROVIDER):
        """Create a provider user."""
        user = super().create_user(
            username=username,
            email=email,
            password=password,
            role=role,
        )
        ProviderProfile.objects.create(user=user)
        return user
