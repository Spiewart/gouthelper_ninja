import uuid

from django.db import models


class GoutHelperModel(models.Model):
    """
    Model Mixin to add UUID field for objects.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    objects = models.Manager()

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
