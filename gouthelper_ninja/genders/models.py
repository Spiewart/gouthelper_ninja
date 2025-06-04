from typing import Literal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from rules.contrib.models import RulesModelBase
from rules.contrib.models import RulesModelMixin
from simple_history.models import HistoricalRecords

from gouthelper_ninja.genders.choices import Genders
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
