from typing import TYPE_CHECKING
from typing import Self

from django.core.exceptions import FieldDoesNotExist
from django.db.models import ForeignKey
from django.db.models import ManyToManyField
from django.db.models import Model
from django.db.models import OneToOneField
from django.db.models import OneToOneRel
from pydantic import BaseModel as Schema

if TYPE_CHECKING:
    from django.db.models import Field  # pragma: no_cover


class GoutHelperCrudMixin:
    """Mixin to add CRUD methods to GoutHelper models."""

    # Flags to indicate if the model needs to be saved or deleted
    # These are used to track changes in the model and can be set by the service layer
    save_needed: bool = False
    delete_needed: bool = False

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
