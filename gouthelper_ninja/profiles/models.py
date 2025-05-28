from django.conf import settings
from django.db import models
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel
from rules.contrib.models import RulesModelBase
from rules.contrib.models import RulesModelMixin
from simple_history.models import HistoricalRecords

from gouthelper_ninja.utils.helpers import get_user_change
from gouthelper_ninja.utils.models import GoutHelperModel


class Profile(
    RulesModelMixin,
    GoutHelperModel,
    TimeStampedModel,
    metaclass=RulesModelBase,
):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.user.username + "'s Profile")

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.user_username})


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
        editable=False,
    )
    history = HistoricalRecords(get_user=get_user_change)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(provider__isnull=False, provider_alias__isnull=False)
                    | models.Q(provider__isnull=True, provider_alias__isnull=True)
                ),
                name="%(class)s_alias_required_for_provider",
            ),
        ]


class ProviderProfile(Profile):
    """Provider User Profile.
    Meant for providers who want to keep track of their patients GoutHelper data.
    """

    history = HistoricalRecords(get_user=get_user_change)
