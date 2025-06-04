import uuid

from django.db.models import Manager
from django.db.models import Model
from django.db.models import UUIDField


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
