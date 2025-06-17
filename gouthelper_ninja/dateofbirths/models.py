from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from rules.contrib.models import RulesModelBase
from rules.contrib.models import RulesModelMixin
from simple_history.models import HistoricalRecords

from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.utils.models import GoutHelperModel

User = get_user_model()


# Create your models here.
class DateOfBirth(
    RulesModelMixin,
    GoutHelperModel,
    TimeStampedModel,
    metaclass=RulesModelBase,
):
    """Model definition for DateOfBirth."""

    dateofbirth = models.DateField(
        _("Age"),
        # TODO: Add a link to the about page
        help_text="How old is the patient (range: 18-120)?",
    )
    patient = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)
    history = HistoricalRecords()

    edit_schema = DateOfBirthEditSchema

    class Meta:
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

    def __str__(self):
        """Unicode representation of DateOfBirth."""
        return f"{self.dateofbirth}"

    def get_absolute_url(self):
        """Return the absolute URL for the DateOfBirth instance."""
        return self.patient.get_absolute_url()

    def update(self, data: DateOfBirthEditSchema) -> "DateOfBirth":
        """Update the DateOfBirth instance with the given kwargs."""

        dob = data.dateofbirth
        if dob != self.dateofbirth:
            self.dateofbirth = dob
            self.full_clean()
            self.save()
        return self
