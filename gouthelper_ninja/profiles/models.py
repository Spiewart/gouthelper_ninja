from django.conf import settings
from django.db import models
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from gouthelper_ninja.profiles.helpers import get_user_change
from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.rules import delete_object
from gouthelper_ninja.rules import view_object
from gouthelper_ninja.utils.models import GoutHelperModel


class Profile(
    GoutHelperModel,
    TimeStampedModel,
):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    class Meta(GoutHelperModel.Meta):
        abstract = True

    def __str__(self):
        return str(self.user.username + "'s Profile")

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.user.username})


class AdminProfile(Profile):
    """Admin User Profile. Meant for superusers, organizational staff who are
    not explicitly providers, or contributors to GoutHelper.
    """

    history = HistoricalRecords(get_user=get_user_change)


class PatientProfile(Profile):
    """Profile for a real (to be implemented) or hypothetical patient."""

    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="pseudopatient_profiles",
        null=True,
        blank=True,
        default=None,
    )
    provider_alias = models.IntegerField(
        null=True,
        blank=True,
        default=None,
    )
    history = HistoricalRecords(get_user=get_user_change)

    class Meta(Profile.Meta):
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(provider__isnull=False, provider_alias__isnull=False)
                    | models.Q(provider__isnull=True)
                ),
                name="%(class)s_alias_required_for_provider",
            ),
        ]
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class ProviderProfile(Profile):
    """Provider User Profile.
    Meant for providers who want to keep track of their patients GoutHelper data.
    """

    history = HistoricalRecords(get_user=get_user_change)
