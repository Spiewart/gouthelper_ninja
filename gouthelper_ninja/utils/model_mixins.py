from pydantic import BaseModel as Schema

from gouthelper_ninja.utils.managers import GoutHelperManager


class GoutHelperCrudMixin:
    """Mixin to add CRUD methods to GoutHelper models."""

    # Flags to indicate if the model needs to be saved or deleted
    # These are used to track changes in the model and can be set by the service layer
    save_needed: bool = False
    delete_needed: bool = False
    objects = GoutHelperManager()

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

    def gh_update(self, data: Schema | dict, **kwargs) -> "GoutHelperCrudMixin":
        """Updates the Model instance and related models using
        data via a Pydantic Schema. Schema fields are Model fields
        or related models with their respective editing Schema."""
        return self.__class__.objects.gh_update(self, data, **kwargs)
