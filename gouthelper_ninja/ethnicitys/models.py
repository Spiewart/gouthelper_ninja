from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.ethnicitys.schema import EthnicityEditSchema
from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.rules import delete_object
from gouthelper_ninja.rules import view_object
from gouthelper_ninja.utils.helpers import get_user_change
from gouthelper_ninja.utils.models import GoutHelperModel

User = get_user_model()


class Ethnicity(
    GoutHelperModel,
    TimeStampedModel,
):
    Ethnicitys = Ethnicitys

    ethnicity = models.CharField(
        _("Ethnicity or Race"),
        max_length=40,
        choices=Ethnicitys.choices,
        help_text="What is the patient's ethnicity or race?",
    )
    patient = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)
    history = HistoricalRecords(get_user=get_user_change)

    edit_schema = EthnicityEditSchema

    class Meta(GoutHelperModel.Meta):
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ethnicity__in=Ethnicitys.values),
                name="ethnicity_valid",
            ),
        ]
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    def __str__(self):
        return self.get_ethnicity_display()

    def get_absolute_url(self):
        """Returns the absolute URL for the Ethnicity's patient."""
        return self.patient.get_absolute_url()

    def update(self, data: EthnicityEditSchema) -> "Ethnicity":
        """Update the Ethnicity instance using Pydantic schema."""

        return super().update(data=data)
