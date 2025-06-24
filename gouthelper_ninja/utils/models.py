import uuid
from typing import TYPE_CHECKING

from django.db.models import Manager
from django.db.models import Model
from django.db.models import UUIDField

if TYPE_CHECKING:
    from django.db.models import Field
    from pydantic import BaseModel as Schema


class GoutHelperModel(Model):
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

    def update(self, data: "Schema") -> Model:
        """Updates the Model instance and related models.
        Schema fields are Model fields or related models
        with their respective editing Schema."""

        for attr_name, attr_data in data.dict().items():
            attr: Model | Field = getattr(self, attr_name)
            if isinstance(attr, Model):
                attr.update(data=attr.edit_schema(**attr_data))
            else:
                attr_val = getattr(self, attr_name, None)
                if attr_val != attr_data:
                    setattr(self, attr_name, attr_data)
                    self.save_needed = True

        if self.save_needed:
            self.full_clean()
            self.save()

        return self


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
