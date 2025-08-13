from django.contrib.auth import get_user_model
from django.db.models import CASCADE
from django.db.models import CheckConstraint
from django.db.models import OneToOneField
from django.db.models import Q
from django.db.models.fields import BooleanField
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from gouthelper_ninja.choices import BOOL_CHOICES
from gouthelper_ninja.goutdetails.schema import GoutDetailEditSchema
from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.rules import delete_object
from gouthelper_ninja.rules import view_object
from gouthelper_ninja.utils.helpers import get_user_change
from gouthelper_ninja.utils.models import GoutHelperModel

User = get_user_model()


class GoutDetail(
    GoutHelperModel,
    TimeStampedModel,
):
    """Describes whether a Patient with a history of gout is actively
    flaring or hyperuricemic (defined as in the past 6 months)."""

    class Meta:
        constraints = [
            CheckConstraint(
                name="%(class)s_at_goal_valid",
                condition=(
                    Q(
                        at_goal__isnull=False,
                        at_goal=False,
                        at_goal_long_term=False,
                    )
                    | Q(
                        at_goal__isnull=False,
                        at_goal=True,
                    )
                    | Q(
                        at_goal__isnull=True,
                        at_goal_long_term=False,
                    )
                ),
            ),
        ]
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    at_goal = BooleanField(
        choices=BOOL_CHOICES,
        help_text=(
            "Is the patient at goal uric acid level? Goal is typically < 6.0 mg/dL."
        ),
        null=True,
        blank=True,
        default=None,
    )
    at_goal_long_term = BooleanField(
        choices=BOOL_CHOICES,
        help_text="Has the patient been at goal uric acid six months or longer? \
Goal is typically < 6.0 mg/dL.",
        default=False,
    )
    flaring = BooleanField(
        choices=BOOL_CHOICES,
        help_text="Any recent gout flares?",
        null=True,
        blank=True,
        default=None,
    )
    on_ppx = BooleanField(
        _("On PPx?"),
        choices=BOOL_CHOICES,
        help_text="Is the patient on flare prophylaxis therapy?",
        default=False,
    )
    on_ult = BooleanField(
        _("On ULT?"),
        choices=BOOL_CHOICES,
        help_text="Is the patient on or starting ULT (urate-lowering therapy)?",
        default=False,
    )
    starting_ult = BooleanField(
        _("Starting Urate-Lowering Therapy (ULT)"),
        choices=BOOL_CHOICES,
        default=False,
        help_text="Is the patient starting ULT or is he or she still in the initial \
dose adjustment (titration) phase?",
    )
    patient = OneToOneField(User, on_delete=CASCADE, editable=False)
    history = HistoricalRecords(get_user=get_user_change)

    edit_schema = GoutDetailEditSchema

    def get_absolute_url(self):
        """Returns the absolute URL for the Ethnicity's patient."""
        return self.patient.get_absolute_url()
