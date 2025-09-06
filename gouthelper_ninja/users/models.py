import uuid
from typing import TYPE_CHECKING
from typing import Self
from typing import Union

from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import FieldDoesNotExist
from django.db.models import CharField
from django.db.models import CheckConstraint
from django.db.models import ForeignKey
from django.db.models import IntegerField
from django.db.models import ManyToManyField
from django.db.models import Model
from django.db.models import OneToOneField
from django.db.models import OneToOneRel
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

if TYPE_CHECKING:
    from pydantic import BaseModel as Schema

    from gouthelper_ninja.medhistorys.models import MedHistory


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

    # Flags to indicate if the model needs to be saved or deleted
    # These are used to track changes in the model and can be set by the service layer
    save_needed = False
    delete_needed = False

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
        # Swap the class back to User to trigger saving the
        # history model correctly (HistoricalUser)
        # and then change it back to the specific role model
        self.__class__ = User
        self.save_needed = False
        super().save(*args, **kwargs)
        # The Pseudopatient role does not have a separate model,
        # so we need to change the class to Patient if the role is Pseudopatient.
        role = (
            Roles.PATIENT.name.lower()
            if self.role == Roles.PSEUDOPATIENT
            else (self.Roles(self.role).name.lower())
        )
        self.__class__ = apps.get_model(f"users.{role}")

    def delete(self, *args, **kwargs):
        """
        Override delete method to remove the delete_needed flag.
        """
        self.delete_needed = False
        super().delete(*args, **kwargs)

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
    def ckd(self) -> Union["MedHistory", None]:
        """The Patient's CKD MedHistory or None if
        it does not exist."""
        return self.get_medhistory(MHTypes.CKD)

    @cached_property
    def diabetes(self) -> Union["MedHistory", None]:
        """The Patient's diabetes MedHistory or None if
        it does not exist."""
        return self.get_medhistory(MHTypes.DIABETES)

    @cached_property
    def erosions(self) -> Union["MedHistory", None]:
        """The Patient's erosions MedHistory or None if
        it does not exist."""
        return self.get_medhistory(MHTypes.EROSIONS)

    @cached_property
    def gout(self) -> Union["MedHistory", None]:
        """The Patient's gout MedHistory or None if
        it does not exist."""
        return self.get_medhistory(MHTypes.GOUT)

    @cached_property
    def hyperuricemia(self) -> Union["MedHistory", None]:
        """The Patient's hyperuricemia MedHistory or None if
        it does not exist."""
        return self.get_medhistory(MHTypes.HYPERURICEMIA)

    @cached_property
    def menopause(self) -> Union["MedHistory", None]:
        """The Patient's menopause MedHistory or None if
        it does not exist."""
        return self.get_medhistory(MHTypes.MENOPAUSE)

    @cached_property
    def tophi(self) -> Union["MedHistory", None]:
        """The Patient's tophi MedHistory or None if
        it does not exist."""
        return self.get_medhistory(MHTypes.TOPHI)

    @cached_property
    def uratestones(self) -> Union["MedHistory", None]:
        """The Patient's uratestones MedHistory or None if
        it does not exist."""
        return self.get_medhistory(MHTypes.URATESTONES)

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

    def update_or_create_relation(
        self,
        field_name: str,
        field_data: Union["Schema", dict | None],
    ) -> Model | None:
        if hasattr(self, field_name):
            obj = getattr(self, field_name, None)
            # OneToOne or faux-OneToOne Patient object's will never be
            # deleted (save for with deletion of the Patient)
            if obj is not None and field_data is not None:
                obj.gh_update(data=field_data)
            # MedHistorys getter should return None and True for hasattr
            # thus should be created if there is data
            elif field_data is not None:
                # TODO: add model to Schema, use to create
                obj = apps.get_model(
                    "medhistorys",
                    f"{field_name}",
                ).objects.gh_create(data=field_data, patient=self)
        elif field_data:
            # If the field is a OneToOne relationship that doesn't exist,
            # create it
            obj = apps.get_model(
                f"{field_name}s",
                f"{field_name}",
            ).objects.gh_create(data=field_data, patient=self)
        else:
            obj = None
        return obj


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

    def gh_update(self, data: Union["Schema", dict]) -> Self:
        """Updates the Model instance and related models using
        data via a Pydantic Schema. Schema fields are Model fields
        or related models with their respective editing Schema."""

        if not isinstance(data, dict):
            data = data.model_dump()

        for field_name, field_data in data.items():
            self.process_schema_field(field_name, field_data)
        if self.save_needed:
            self.full_clean()
            self.save()
        return self

    def process_schema_field(
        self,
        field_name: str,
        field_data: Union["Schema", dict, None],
    ) -> None:
        # Check if the Schema is a Patient relationship
        if field_data and (
            hasattr(self, field_name) or self.field_is_onetoone(field_name)
        ):
            self.update_or_create_relation(field_name, field_data)
        else:
            # Check if the Schema field is a Model or Field
            attr: Model = getattr(self, field_name)
            # If it's a Model, update it with the Schema data
            if isinstance(attr, Model) and field_data is not None:
                attr.gh_update(data=field_data)
            # Otherwise, it's a Field, so set the value directly
            else:
                attr_val = getattr(self, field_name, None)
                # If the value is different, set it and mark the model as
                # needing to be saved
                if attr_val != field_data:
                    setattr(self, field_name, field_data)
                    self.save_needed = True

    @classmethod
    def field_is_related_model(cls, field_name: str) -> bool:
        """Check if the field is a OneToOne, ForeignKey, or ManyToMany
        relationship."""
        try:
            field = cls._meta.get_field(field_name)
        except FieldDoesNotExist:
            return False
        return isinstance(
            field,
            (
                OneToOneField,
                ForeignKey,
                ManyToManyField,
            ),
        )

    @classmethod
    def field_is_onetoone(cls, field_name: str) -> bool:
        """Check if the field is a OneToOne relationship."""
        try:
            field = cls._meta.get_field(field_name)
        except FieldDoesNotExist:
            return False
        return isinstance(field, (OneToOneField, OneToOneRel))


class Provider(User):
    # This sets the user type to PROVIDER during record creation
    base_role = User.Roles.PROVIDER

    # Ensures queries on the Provider model return only Providers
    objects = ProviderManager()

    class Meta(User.Meta):
        proxy = True
