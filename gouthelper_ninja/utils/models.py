import uuid
from typing import TYPE_CHECKING
from typing import Self

from django.core.exceptions import FieldDoesNotExist
from django.db.models import CASCADE
from django.db.models import ForeignKey
from django.db.models import ManyToManyField
from django.db.models import Model
from django.db.models import OneToOneField
from django.db.models import OneToOneRel
from django.db.models import UUIDField
from django_extensions.db.models import TimeStampedModel
from pydantic import BaseModel as Schema
from rules.contrib.models import RulesModelBase
from rules.contrib.models import RulesModelMixin
from simple_history.models import HistoricalRecords

from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.rules import delete_object
from gouthelper_ninja.rules import view_object
from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.utils.helpers import get_user_change
from gouthelper_ninja.utils.managers import GoutHelperManager

if TYPE_CHECKING:
    from django.db.models import Field  # pragma: no_cover


class GoutHelperOneToOne(
    TimeStampedModel,
    RulesModelMixin,
    Model,
    metaclass=RulesModelBase,
):
    """
    Model Mixin to add UUID field for objects.
    """

    id = UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    patient = OneToOneField(
        Patient,
        on_delete=CASCADE,
        editable=False,
    )
    objects = GoutHelperManager()
    history = HistoricalRecords(get_user=get_user_change, inherit=True)

    # Flags to indicate if the model needs to be saved or deleted
    # These are used to track changes in the model and can be set by the service layer
    save_needed = False
    delete_needed = False

    class Meta:
        abstract = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "read": view_object,
        }

    def save(self, *args, **kwargs):
        """
        Override save method to remove the save_needed flag.
        """
        self.save_needed = False
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Override delete method to remove the delete_needed flag.
        """
        self.delete_needed = False
        super().delete(*args, **kwargs)

    def gh_update(self, data: Schema | dict) -> Self:
        """Updates the Model instance and related models using
        data via a Pydantic Schema. Schema fields are Model fields
        or related models with their respective editing Schema."""
        if isinstance(data, Schema):
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
        field_data: Schema | dict | None,
    ) -> None:
        # Check if the Schema is a Patient relationship
        if (
            field_data
            and hasattr(self, "patient")
            and field_name != self.__class__.__name__.lower()
            and (
                hasattr(self.patient, field_name)
                or self.patient.field_is_onetoone(field_name)
            )
        ):
            self.patient.update_or_create_relation(field_name, field_data)
        else:
            # Check if the Schema field is a Model or Field
            attr: Model | Field = getattr(self, field_name)
            # If it's a Model, update it with the Schema data
            if isinstance(attr, Model) and field_data is not None:
                attr.gh_update(data=attr.edit_schema(**field_data))
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


class GetStrAttrsMixin:
    """Adds methods for setting str_attrs to any object and fetching them
    using get_str_attrs method."""

    str_attrs: dict[str, str]

    def get_str_attrs(
        self,
        *args: tuple[str],
    ) -> tuple[str]:
        """Takes any Literal str args and returns a tuple of strs for use as text in
        HTML UI."""

        return tuple(self.str_attrs[arg] for arg in args)
