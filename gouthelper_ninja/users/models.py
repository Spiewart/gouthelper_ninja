from typing import TYPE_CHECKING
from typing import Union

from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models import CheckConstraint
from django.db.models import IntegerField
from django.db.models import Q
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.medhistorys.helpers import search_medhistorys_by_mhtype
from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.helpers import get_user_change
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
from gouthelper_ninja.users.schema import PatientEditSchema
from gouthelper_ninja.utils.models import GoutHelperModel

if TYPE_CHECKING:
    from gouthelper_ninja.medhistorys.models import MedHistory


class User(
    GoutHelperModel,
    TimeStampedModel,
    AbstractUser,
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
        if self.role in [Roles.PATIENT, Roles.PSEUDOPATIENT]:
            return reverse("users:patient-detail", kwargs={"patient": self.id})
        return reverse("users:detail", kwargs={"username": self.username})

    def save(self, *args, **kwargs):
        # If a new user, set the user's role based off the
        # base_role property
        if not self.pk and hasattr(self, "base_role"):
            self.role = self.base_role
        # Swap the class back to User to trigger saving the
        # history model correctly (HistoricalUser)
        # and then change it back to the specific role model
        self.__class__ = User
        super().save(*args, **kwargs)
        # The Pseudopatient role does not have a separate model,
        # so we need to change the class to Patient if the role is Pseudopatient.
        role = (
            Roles.PATIENT.name.lower()
            if self.role == Roles.PSEUDOPATIENT
            else (self.Roles(self.role).name.lower())
        )
        self.__class__ = apps.get_model(f"users.{role}")

    @cached_property
    def creator(self) -> Union["User", None]:
        """Returns the first history's history_user, which if
        present, is the user that created this User instance."""
        return (
            self.history.select_related(
                "history_user",
            )
            .order_by("history_date")
            .first()
            .history_user
        )

    @cached_property
    def diabetes(self) -> Union["MedHistory", None]:
        """The Patient's diabetes MedHistory or None if
        it does not exist."""
        return self.get_medhistory(MHTypes.DIABETES)

    @cached_property
    def gout(self) -> Union["MedHistory", None]:
        """The Patient's gout MedHistory or None if
        it does not exist."""
        return self.get_medhistory(MHTypes.GOUT)

    def get_medhistory(self, mhtype: "MHTypes") -> Union["MedHistory", None]:
        """Returns the instance's MedHistory of the given type,
        if it exists. Raises AttributeError if the User is not a Patient."""
        if self.role not in [self.Roles.PATIENT, self.Roles.PSEUDOPATIENT]:
            msg = _(
                f"User {self} is not a Patient, cannot get "  # noqa: INT001
                f"MedHistory of type {mhtype}.",
            )
            raise AttributeError(
                msg,
            )
        return (
            search_medhistorys_by_mhtype(
                self.medhistorys_qs,
                mhtype,
            )
            if hasattr(self, "medhistorys_qs")
            else search_medhistorys_by_mhtype(
                self.medhistory_set.all(),
                mhtype,
            )
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


class Patient(User):
    # This sets the user type to PSEUDOPATIENT during record creation
    base_role = User.Roles.PSEUDOPATIENT

    # Ensures queries on the Pseudopatient model return only Pseudopatients
    objects = PatientManager()

    edit_schema = PatientEditSchema

    class Meta(User.Meta):
        proxy = True
        rules_permissions = {
            "change": change_patient,
            "delete": delete_patient,
            "view": view_patient,
        }

    def update(self, data: PatientEditSchema) -> "Patient":
        """Updates the Patient instance and related models.
        Overwritten to use PatientEditSchema for validation."""

        return super().update(data=data)


class Provider(User):
    # This sets the user type to PROVIDER during record creation
    base_role = User.Roles.PROVIDER

    # Ensures queries on the Provider model return only Providers
    objects = ProviderManager()

    class Meta(User.Meta):
        proxy = True
