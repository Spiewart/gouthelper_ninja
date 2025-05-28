from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from rules.contrib.models import RulesModelBase
from rules.contrib.models import RulesModelMixin
from simple_history.models import HistoricalRecords

from gouthelper_ninja.ethnicitys.choices import Ethnicitys
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
        help_text=format_lazy(
            # TODO: Add a link to the about page
            """What is the patient's ethnicity or race? <a href="" target="_next">
            Why do we need to know?</a>""",
            # reverse_lazy("ethnicitys:about"),  # noqa: ERA001
        ),
    )
    patient = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ethnicity__in=Ethnicitys.values),
                name="ethnicity_valid",
            ),
        ]

    def __str__(self):
        return self.get_ethnicity_display()
