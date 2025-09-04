from typing import Literal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.schema import GenderEditSchema
from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.rules import delete_object
from gouthelper_ninja.rules import view_object
from gouthelper_ninja.utils.models import GoutHelperOneToOne

User = get_user_model()


class Gender(
    GoutHelperOneToOne,
    TimeStampedModel,
):
    """Model representing biological gender.
    Gender is stored as an integer in gender field. Male=0, Female=1."""

    Genders = Genders

    gender = models.IntegerField(
        _("Biological Sex"),
        choices=Genders.choices,
        help_text="What is the patient's biological sex?",
    )

    edit_schema = GenderEditSchema

    class Meta(GoutHelperOneToOne.Meta):
        constraints = [
            models.CheckConstraint(
                name="gender_valid",
                condition=models.Q(gender__in=Genders.values),
            ),
        ]
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    def __str__(self) -> Genders | Literal["Gender unknown"]:
        if self.gender is not None:
            return self.get_gender_display()
        return "Gender unknown"

    def get_absolute_url(self):
        """Returns the absolute URL for the Ethnicity's patient."""
        return self.patient.get_absolute_url()
