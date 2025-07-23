import uuid
from typing import TYPE_CHECKING

from django.db.models import Manager
from django.db.models import Model
from django.db.models import UUIDField
from rules.contrib.models import RulesModelBase
from rules.contrib.models import RulesModelMixin

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

    def update(self, data: "Schema") -> Model:
        """Updates the Model instance and related models.
        Schema fields are Model fields or related models
        with their respective editing Schema."""

        for attr_name, attr_data in data.model_dump().items():
            attr: Model | Field = getattr(self, attr_name)
            if isinstance(attr, Model) and attr_data is not None:
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
