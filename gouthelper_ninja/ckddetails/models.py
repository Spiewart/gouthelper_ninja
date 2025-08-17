from django.contrib.auth import get_user_model
from django.db.models import CASCADE
from django.db.models import BooleanField
from django.db.models import CheckConstraint
from django.db.models import IntegerField
from django.db.models import OneToOneField
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from gouthelper_ninja.choices import BOOL_CHOICES
from gouthelper_ninja.ckddetails.choices import DialysisChoices
from gouthelper_ninja.ckddetails.choices import DialysisDurations
from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.ckddetails.managers import CkdDetailManager
from gouthelper_ninja.utils.helpers import get_user_change
from gouthelper_ninja.utils.models import GoutHelperModel

User = get_user_model()


class CkdDetail(
    GoutHelperModel,
    TimeStampedModel,
):
    """Describes details of a patient's Chronic Kidney Disease (CKD)."""

    class Meta:
        constraints = [
            CheckConstraint(
                name="%(class)s_dialysis_valid",
                condition=(
                    Q(
                        dialysis=False,
                        dialysis_duration__isnull=True,
                        dialysis_type__isnull=True,
                    )
                    | Q(
                        stage=Stages.FIVE,
                        dialysis=True,
                        dialysis_duration__isnull=False,
                        dialysis_type__isnull=False,
                    )
                ),
            ),
            CheckConstraint(
                name="%(class)s_dialysis_duration_valid",
                condition=(Q(dialysis_duration__in=DialysisDurations.values)),
            ),
            CheckConstraint(
                name="%(class)s_dialysis_type_valid",
                condition=(Q(dialysis_type__in=DialysisChoices.values)),
            ),
            CheckConstraint(
                name="%(class)s_stage_valid",
                condition=(Q(stage__in=Stages.values)),
            ),
        ]

    DialysisChoices = DialysisChoices
    DialysisDurations = DialysisDurations
    Stages = Stages

    dialysis = BooleanField(
        verbose_name=_("Dialysis"),
        choices=BOOL_CHOICES,
        help_text=_(
            "Is the patient on <a href='https://en.wikipedia.org/wiki/Hemodialysis'"
            " target='_blank'>dialysis</a>?",
        ),
        default=False,
    )
    dialysis_duration = IntegerField(
        verbose_name=_("Time on Dialysis"),
        choices=DialysisDurations.choices,
        help_text=_("How long has the patient been on dialysis?"),
        null=True,
        blank=True,
        default=None,
    )
    dialysis_type = IntegerField(
        verbose_name=_("Dialysis Type"),
        choices=DialysisChoices.choices,
        help_text=_("What type of dialysis?"),
        null=True,
        blank=True,
        default=None,
    )
    stage = IntegerField(
        # https://www.kidney.org/kidney-topics/stages-chronic-kidney-disease-ckd
        choices=Stages.choices,
        help_text=_(
            "What <a href='https://www.kidney.org/kidney-topics/stages-chronic-kidney-disease-ckd'"
            " target='_blank'>stage</a> CKD?",
        ),
        verbose_name=_("CKD Stage"),
    )
    patient = OneToOneField(User, on_delete=CASCADE, editable=False)
    history = HistoricalRecords(get_user=get_user_change)
    objects = CkdDetailManager()

    @property
    def explanation(self):
        if self.dialysis:
            return f"CKD on {self.get_dialysis_type_display().lower()}"
        return f"CKD stage {self.get_stage_display()}"

    def __str__(self):
        return f"CKD {self.dialysis_type if self.dialysis else self.stage}"
