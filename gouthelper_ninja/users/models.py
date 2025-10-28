import uuid
from typing import TYPE_CHECKING
from typing import Union

from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models import CheckConstraint
from django.db.models import IntegerField
from django.db.models import Model
from django.db.models import Q
from django.db.models import UUIDField
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from rules.contrib.models import RulesModelBase
from rules.contrib.models import RulesModelMixin
from simple_history.models import HistoricalRecords

from gouthelper_ninja.medhistorys.choices import MHTypes
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
from gouthelper_ninja.utils.model_mixins import GoutHelperCrudMixin

if TYPE_CHECKING:
    from pydantic import BaseModel as Schema


class User(
    RulesModelMixin,
    TimeStampedModel,
    AbstractUser,
    metaclass=RulesModelBase,
):
    """
    Default custom user model for gouthelper.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    id = UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    Roles = Roles

    # Cookiecutter defaults
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    # GoutHelper specific fields
    role = IntegerField(_("Role"), choices=Roles.choices, default=Roles.PROVIDER)
    # GoutHelper managers and other attributes
    objects: GoutHelperUserManager = GoutHelperUserManager()
    history = HistoricalRecords(
        get_user=get_user_change,
        inherit=True,
    )

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
        # Respect historical subclasses by ensuring the class is correct
        class_for_role = self.get_class()
        if self.__class__ != class_for_role:
            self.__class__ = class_for_role
        self.save_needed = False
        super().save(*args, **kwargs)

    def get_class(
        self,
    ) -> type["User"] | type["Admin"] | type["Provider"] | type["Patient"]:
        """Returns the class of the specific user instance."""
        # The Pseudopatient role does not have a separate model,
        # so we need to change the class to Patient if the role is
        # Pseudopatient.
        role = (
            Roles.PATIENT.name.lower()
            if self.role == Roles.PSEUDOPATIENT
            else (self.Roles(self.role).name.lower())
        )
        return apps.get_model(f"users.{role}")

    def delete(self, *args, **kwargs):
        """
        Override delete method to remove the delete_needed flag.
        """
        # Respect historical subclasses by ensuring the class is correct
        class_for_role = self.get_class()
        if self.__class__ != class_for_role:
            self.__class__ = class_for_role
        self.delete_needed = False
        super().delete(*args, **kwargs)


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


class Patient(GoutHelperCrudMixin, User):
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

    @classmethod
    def get_related_model_field(cls, field_name: str):
        """If the parent method does not return a Field, check if the
        field_name is in MedHistorys and return that Field if so."""
        field = super().get_related_model_field(field_name)
        if field is None:
            mhtype = next(iter(MHTypes), None)
            if mhtype:
                field = apps.get_model(
                    "medhistorys",
                    f"{field_name.lower()}",
                )
        return field

    def process_null_related_model_field_data(
        self,
        field_name: str,
    ) -> None:
        """Processes null data for an exising related model field instance."""
        # For Patient, we do not want to delete related model instances
        # (i.e. MedHistorys) when null data is provided. Instead, we
        # simply ignore the null data.

    def update_or_create_relation(
        self,
        relation_name: str,
        relation_data: Union["Schema", dict],
    ) -> Model | None:
        obj = getattr(self, relation_name, None)
        if obj is not None:
            return obj.gh_update(data=relation_data)
        field = self.get_related_model_field(relation_name)
        if field:
            if self.schema_field_is_onetoone(relation_name):
                obj = field.related_model.objects.gh_create(
                    data=relation_data,
                    patient=self,
                )
        else:
            # Otherwise, the relation is a MedHistory
            obj = apps.get_model(
                "medhistorys",
                f"{relation_name}",
            ).objects.gh_create(data=relation_data, patient=self)
        return obj

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


class Provider(User):
    # This sets the user type to PROVIDER during record creation
    base_role = User.Roles.PROVIDER

    # Ensures queries on the Provider model return only Providers
    objects = ProviderManager()

    class Meta(User.Meta):
        proxy = True
