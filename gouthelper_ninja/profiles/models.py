from typing import TYPE_CHECKING
from typing import Union

from django.conf import settings
from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords

from gouthelper_ninja.profiles.helpers import get_user_change
from gouthelper_ninja.profiles.managers import PatientProfileManager
from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.rules import delete_object
from gouthelper_ninja.rules import view_object
from gouthelper_ninja.utils.models import AdminOneToOne
from gouthelper_ninja.utils.models import PatientOneToOne
from gouthelper_ninja.utils.models import ProviderOneToOne

if TYPE_CHECKING:
    from gouthelper_ninja.users.models import Admin
    from gouthelper_ninja.users.models import Patient
    from gouthelper_ninja.users.models import Provider


class Profile(models.Model):
    user: Union["Patient", "Provider", "Admin"]
    history = HistoricalRecords(get_user=get_user_change, inherit=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.user.username + "'s Profile")

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.user.username})


class AdminProfile(AdminOneToOne, Profile):
    """Admin User Profile. Meant for superusers, organizational staff who are
    not explicitly providers, or contributors to GoutHelper.
    """

    class Meta(Profile.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    @property
    def user(self):
        return self.admin


class PatientProfile(PatientOneToOne, Profile):
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
    objects = PatientProfileManager()

    class Meta(Profile.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    @property
    def user(self):
        return self.patient


class ProviderProfile(ProviderOneToOne, Profile):
    """Provider User Profile.
    Meant for providers who want to keep track of their patients GoutHelper data.
    """

    class Meta(Profile.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    def __str__(self):
        return str(self.provider.username + "'s Profile")
