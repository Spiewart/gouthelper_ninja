from typing import TYPE_CHECKING
from typing import Any
from typing import Union
from uuid import uuid4

from django.apps import apps
from django.contrib.auth.base_user import BaseUserManager

from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.utils.managers import GoutHelperCRUD
from gouthelper_ninja.utils.managers import GoutHelperManager

if TYPE_CHECKING:
    from django.db.models import Model

    from gouthelper_ninja.users.models import Patient


class PatientCrud(GoutHelperCRUD):
    def get_crud_kwargs(self, **kwargs) -> dict[str, Any]:
        return {**kwargs}

    def get_patient_data(self) -> dict[str, Any] | None:
        return None

    def get_or_create_patient(self, patient: Union["Patient", None] = None) -> None:
        return None

    def process_null_forward_relation(
        self,
        relation_name: str,
    ) -> None:
        """Process null forward relations for OneToOne and ForeignKey fields."""

    def process_null_reverse_relation(
        self,
        relation_name: str,
    ) -> None:
        """Process null reverse relations for OneToOne and ForeignKey fields."""


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
        admin = self.model(
            email=email,
            is_staff=True,
            is_superuser=True,
            role=role,
            **extra_fields,
        )
        admin.set_password(password)
        admin.save()
        apps.get_model("profiles", "AdminProfile").objects.create(admin=admin)
        return admin


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
        apps.get_model("profiles", "AdminProfile").objects.create(admin=user)
        return user


class PatientManager(GoutHelperUserManager, GoutHelperManager):
    CRUD_SERVICE = PatientCrud

    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=Roles.PSEUDOPATIENT)

    def create(self, **kwargs) -> "Model":
        return super().create(
            role=Roles.PSEUDOPATIENT,
            username=uuid4().hex[:30],
            **kwargs,
        )

    def gh_update(
        self,
        instance,
        data,
        **kwargs,
    ):
        return self.CRUD_SERVICE(
            manager=self,
            data=data,
            instance=instance,
            patient=None,
            **kwargs,
        ).gh_update()


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
        apps.get_model("profiles", "ProviderProfile").objects.create(provider=user)
        return user
