from typing import TYPE_CHECKING

from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models import CheckConstraint
from django.db.models import IntegerField
from django.db.models import Model
from django.db.models import Q
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from rules.contrib.models import RulesModelBase
from rules.contrib.models import RulesModelMixin
from simple_history.models import HistoricalRecords

from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.managers import AdminManager
from gouthelper_ninja.users.managers import GoutHelperUserManager
from gouthelper_ninja.users.managers import PatientManager
from gouthelper_ninja.users.managers import ProviderManager
from gouthelper_ninja.users.rules import change_patient
from gouthelper_ninja.users.rules import change_user
from gouthelper_ninja.users.rules import delete_patient
from gouthelper_ninja.users.rules import delete_user
from gouthelper_ninja.users.rules import view_patient
from gouthelper_ninja.users.rules import view_user
from gouthelper_ninja.utils.helpers import get_user_change
from gouthelper_ninja.utils.models import GoutHelperModel

if TYPE_CHECKING:
    from django.db.models import Field


class User(
    RulesModelMixin,
    GoutHelperModel,
    TimeStampedModel,
    AbstractUser,
    metaclass=RulesModelBase,
):
    """
    Default custom user model for gouthelper.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    class Meta:
        constraints = [
            CheckConstraint(
                name="%(app_label)s_%(class)s_role_valid",
                condition=(Q(role__in=Roles.values)),
            ),
        ]
        rules_permissions = {
            "change": change_user,
            "delete": delete_user,
            "view": view_user,
        }

    Roles = Roles

    # Cookiecutter defaults
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    # GoutHelper specific fields
    role = IntegerField(_("Role"), choices=Roles.choices, default=Roles.PROVIDER)
    # GoutHelper managers and other attributes
    objects = GoutHelperUserManager()
    history = HistoricalRecords(
        get_user=get_user_change,
    )

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def save(self, *args, **kwargs):
        # If a new user, set the user's role based off the
        # base_role property
        if not self.pk and hasattr(self, "base_role"):
            self.role = self.base_role
        self.__class__ = User
        super().save(*args, **kwargs)
        role = (
            Roles.PATIENT.name.lower()
            if self.role == Roles.PSEUDOPATIENT
            else (self.Roles(self.role).name.lower())
        )
        self.__class__ = apps.get_model(f"users.{role}")

    @cached_property
    def profile(self):
        role = (
            self.Roles.PATIENT
            if self.role in {self.Roles.PSEUDOPATIENT, self.Roles.PATIENT}
            else self.Roles(self.role)
        )
        return getattr(
            self,
            (f"{role.name.lower()}profile"),
            None,
        )


class Admin(User):
    # This sets the user type to ADMIN during record creation
    base_role = User.Roles.ADMIN

    # Ensures queries on the ADMIN model return only Providers
    objects = AdminManager()

    class Meta(User.Meta):
        proxy = True
        rules_permissions = {
            "change": change_user,
            "delete": delete_user,
            "view": view_user,
        }

    @cached_property
    def profile(self):
        return getattr(self, "adminprofile", None)


class Patient(User):
    # This sets the user type to PSEUDOPATIENT during record creation
    base_role = User.Roles.PSEUDOPATIENT

    # Ensures queries on the Pseudopatient model return only Pseudopatients
    objects = PatientManager()

    class Meta(User.Meta):
        proxy = True
        rules_permissions = {
            "change": change_patient,
            "delete": delete_patient,
            "view": view_patient,
        }

    @cached_property
    def provider(self) -> User | None:
        return getattr(self.profile, "provider", None)

    @cached_property
    def editors(self) -> list[User]:
        """Returns a list of Users who have edited the Patient."""

        return [
            history.history_user
            for history in self.history.select_related(
                "history_user",
            )
            .filter(
                history_user__isnull=False,
            )
            .order_by("history_date")
        ]

    @property
    def creator(self) -> User | None:
        """Returns the User who created the Patient, if available."""
        return self.editors[0] if self.editors else None

    def update(self, **kwargs) -> "Patient":
        """Updates the Patient instance and related models."""

        for key, val in kwargs.items():
            attr: Model | Field = getattr(self, key)
            if isinstance(attr, Model):
                if getattr(attr, key) != val:
                    setattr(attr, key, val)
                    attr.full_clean()
                    attr.save()
            else:
                setattr(self, key, val)
                self.save_needed = True

        if self.save_needed:
            self.full_clean()
            self.save()

        return self

    def get_absolute_url(self) -> str:
        """Get URL for patient's detail view.

        Returns:
            str: URL for patient detail.

        """
        return reverse("users:patient-detail", kwargs={"patient": self.pk})


class Provider(User):
    # This sets the user type to PROVIDER during record creation
    base_role = User.Roles.PROVIDER

    # Ensures queries on the Provider model return only Providers
    objects = ProviderManager()

    class Meta(User.Meta):
        proxy = True

    @cached_property
    def profile(self):
        return getattr(self, "providerprofile", None)
