from typing import Literal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from rules.contrib.models import RulesModelBase
from rules.contrib.models import RulesModelMixin
from simple_history.models import HistoricalRecords

from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.schema import GenderEditSchema
from gouthelper_ninja.utils.models import GoutHelperModel

User = get_user_model()


class Gender(
    RulesModelMixin,
    GoutHelperModel,
    TimeStampedModel,
    metaclass=RulesModelBase,
):
    """Model representing biological gender.
    Gender is stored as an integer in gender field. Male=0, Female=1."""

    Genders = Genders

    gender = models.IntegerField(
        _("Biological Sex"),
        choices=Genders.choices,
        help_text="What is the patient's biological sex?",
    )
    patient = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)
    history = HistoricalRecords()

    edit_schema = GenderEditSchema

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(gender__in=Genders.values),
                name="gender_valid",
            ),
        ]

    def __str__(self) -> Genders | Literal["Gender unknown"]:
        if self.gender is not None:
            return self.get_gender_display()
        return "Gender unknown"

    def get_absolute_url(self):
        """Returns the absolute URL for the Ethnicity's patient."""
        return self.patient.get_absolute_url()

    def update(self, data: GenderEditSchema) -> "Gender":
        """Update the Gender instance with the given kwargs."""

        gender = data.gender
        if gender != self.gender:
            self.gender = gender
            self.full_clean()
            self.save()
        return self
