import uuid

from django.db.models import CASCADE
from django.db.models import Model
from django.db.models import OneToOneField
from django.db.models import UUIDField
from django_extensions.db.models import TimeStampedModel
from rules.contrib.models import RulesModelBase
from rules.contrib.models import RulesModelMixin

from gouthelper_ninja.users.models import Admin
from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.models import Provider
from gouthelper_ninja.utils.managers import GoutHelperManager
from gouthelper_ninja.utils.model_mixins import GoutHelperCrudMixin


class ModelIDMixin(Model):
    """Default ID mixin for all GoutHelper models."""

    id = UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    class Meta:
        abstract = True


class AdminOneToOne(
    GoutHelperCrudMixin,
    TimeStampedModel,
    RulesModelMixin,
    ModelIDMixin,
    metaclass=RulesModelBase,
):
    """
    Model Mixin to add UUID field for objects.
    """

    admin = OneToOneField(
        Admin,
        on_delete=CASCADE,
        editable=False,
    )
    objects = GoutHelperManager()

    class Meta:
        abstract = True


class PatientOneToOne(
    GoutHelperCrudMixin,
    TimeStampedModel,
    RulesModelMixin,
    ModelIDMixin,
    metaclass=RulesModelBase,
):
    """
    Model Mixin to add UUID field for objects.
    """

    patient = OneToOneField(
        Patient,
        on_delete=CASCADE,
        editable=False,
    )
    objects: GoutHelperManager = GoutHelperManager()

    class Meta:
        abstract = True


class ProviderOneToOne(
    GoutHelperCrudMixin,
    TimeStampedModel,
    RulesModelMixin,
    ModelIDMixin,
    metaclass=RulesModelBase,
):
    """
    Model Mixin to add UUID field for objects.
    """

    provider = OneToOneField(
        Provider,
        on_delete=CASCADE,
        editable=False,
    )
    objects = GoutHelperManager()

    class Meta:
        abstract = True


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
