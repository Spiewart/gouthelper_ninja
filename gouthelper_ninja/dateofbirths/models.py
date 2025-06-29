from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.rules import delete_object
from gouthelper_ninja.rules import view_object
from gouthelper_ninja.utils.helpers import get_user_change
from gouthelper_ninja.utils.models import GoutHelperModel

User = get_user_model()


# Create your models here.
class DateOfBirth(
    GoutHelperModel,
    TimeStampedModel,
):
    """Model definition for DateOfBirth."""

    dateofbirth = models.DateField(
        _("Age"),
        # TODO: Add a link to the about page
        help_text="How old is the patient (range: 18-120)?",
    )
    patient = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)
    history = HistoricalRecords(get_user=get_user_change)

    edit_schema = DateOfBirthEditSchema

    class Meta(GoutHelperModel.Meta):
        # GoutHelper is for adults only
        # Date of birth cannot be any year before 18 years ago from now
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    dateofbirth__lte=(
                        models.functions.Now() - timedelta(days=365 * 18)
                    ),
                ),
                name="dateofbirth_valid",
            ),
        ]
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    def __str__(self):
        """Unicode representation of DateOfBirth."""
        return f"{self.dateofbirth}"

    def get_absolute_url(self):
        """Return the absolute URL for the DateOfBirth instance."""
        return self.patient.get_absolute_url()

    def update(self, data: DateOfBirthEditSchema) -> "DateOfBirth":
        """Update the DateOfBirth instance with the given kwargs."""

        return super().update(data=data)
