from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.ethnicitys.schema import EthnicityEditSchema
from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.rules import delete_object
from gouthelper_ninja.rules import view_object
from gouthelper_ninja.utils.models import GoutHelperOneToOne
from gouthelper_ninja.utils.models import HistoryMixin

User = get_user_model()


class Ethnicity(
    GoutHelperOneToOne,
    TimeStampedModel,
    HistoryMixin,
):
    Ethnicitys = Ethnicitys

    ethnicity = models.CharField(
        _("Ethnicity or Race"),
        max_length=40,
        choices=Ethnicitys.choices,
        help_text="What is the patient's ethnicity or race?",
    )

    edit_schema = EthnicityEditSchema

    class Meta(GoutHelperOneToOne.Meta):
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
