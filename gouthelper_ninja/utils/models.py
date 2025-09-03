import uuid
from typing import TYPE_CHECKING
from typing import Self

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Manager
from django.db.models import Model
from django.db.models import OneToOneField
from django.db.models import OneToOneRel
from django.db.models import UUIDField
from rules.contrib.models import RulesModelBase
from rules.contrib.models import RulesModelMixin

from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.rules import delete_object
from gouthelper_ninja.rules import view_object

if TYPE_CHECKING:
    from django.db.models import Field  # pragma: no_cover
    from pydantic import BaseModel as Schema  # pragma: no_cover


class GoutHelperModel(RulesModelMixin, Model, metaclass=RulesModelBase):
    """
    Model Mixin to add UUID field for objects.
    """

    id = UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    objects = Manager()

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

    def gh_update(self, data: "Schema") -> Self:
        """Updates the Model instance and related models using
        data via a Pydantic Schema. Schema fields are Model fields
        or related models with their respective editing Schema."""

        for field_name, field_data in data.model_dump().items():
            self.process_schema_field(field_name, field_data)
        if self.save_needed:
            self.full_clean()
            self.save()
        return self

    def process_schema_field(
        self,
        field_name: str,
        field_data: "Schema",
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
            if hasattr(self.patient, field_name):
                patient_obj = getattr(self.patient, field_name, None)
                # OneToOne or faux-OneToOne Patient object's will never be
                # deleted (save for with deletion of the Patient)
                if patient_obj is not None and field_data is not None:
                    patient_obj.gh_update(data=field_data)
                # MedHistorys getter should return None and True for hasattr
                # thus should be created if there is data
                elif field_data is not None:
                    if field_name in MHTypes.values:
                        apps.get_model(
                            "medhistorys",
                            f"{field_name}",
                        ).objects.gh_create(data=field_data)
            else:
                # If the field is a OneToOne relationship that doesn't exist,
                # create it
                apps.get_model(
                    f"{field_name}s",
                    f"{field_name}",
                ).objects.gh_create(data=field_data)
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

    def field_is_onetoone(self, field_name: str) -> bool:
        """Check if the field is a OneToOne relationship."""
        try:
            field = self._meta.get_field(field_name)
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
