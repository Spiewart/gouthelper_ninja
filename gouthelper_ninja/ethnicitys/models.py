from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from rules.contrib.models import RulesModelBase
from rules.contrib.models import RulesModelMixin
from simple_history.models import HistoricalRecords

from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.ethnicitys.schema import EthnicityEditSchema
from gouthelper_ninja.utils.models import GoutHelperModel

User = get_user_model()


class Ethnicity(
    RulesModelMixin,
    GoutHelperModel,
    TimeStampedModel,
    metaclass=RulesModelBase,
):
    Ethnicitys = Ethnicitys

    ethnicity = models.CharField(
        _("Ethnicity or Race"),
        max_length=40,
        choices=Ethnicitys.choices,
        help_text="What is the patient's ethnicity or race?",
    )
    patient = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)
    history = HistoricalRecords()

    edit_schema = EthnicityEditSchema

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ethnicity__in=Ethnicitys.values),
                name="ethnicity_valid",
            ),
        ]

    def __str__(self):
        return self.get_ethnicity_display()

    def update(self, data: EthnicityEditSchema) -> "Ethnicity":
        """Update the Ethnicity instance with the given kwargs."""

        ethnicity = data.ethnicity
        if ethnicity != self.ethnicity:
            self.ethnicity = ethnicity
            self.full_clean()
            self.save()
        return self
