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

    class Meta:
        abstract = True
