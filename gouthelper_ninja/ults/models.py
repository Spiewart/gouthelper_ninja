from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db.models import CASCADE
from django.db.models import CheckConstraint
from django.db.models import IntegerField
from django.db.models import OneToOneField
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.rules import delete_object
from gouthelper_ninja.rules import view_object
from gouthelper_ninja.ults.choices import FlareFreqs
from gouthelper_ninja.ults.choices import FlareNums
from gouthelper_ninja.ults.choices import Indications
from gouthelper_ninja.utils.models import GoutHelperModel

User = get_user_model()


class Ult(
    GoutHelperModel,
    TimeStampedModel,
):
    class Meta:
        constraints = [
            CheckConstraint(
                name="%(app_label)s_%(class)s_num_flares_valid",
                condition=(Q(num_flares__in=FlareNums.values)),
            ),
            CheckConstraint(
                name="%(app_label)s_%(class)s_freq_flares_valid",
                condition=(Q(freq_flares__in=FlareFreqs.values)),
            ),
            CheckConstraint(
                name="%(app_label)s_%(class)s_indication_valid",
                condition=(Q(indication__in=Indications.values)),
            ),
            CheckConstraint(
                name="%(app_label)s_%(class)s_freq_num_flares_valid",
                condition=(
                    (Q(num_flares=FlareNums.TWOPLUS) & Q(freq_flares__isnull=False))
                    | (Q(num_flares=FlareNums.ONE) & Q(freq_flares__isnull=True))
                    | (Q(num_flares=FlareNums.ZERO) & Q(freq_flares__isnull=True))
                ),
            ),
        ]
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    FlareFreqs = FlareFreqs
    FlareNums = FlareNums
    Indications = Indications

    freq_flares = IntegerField(
        _("Flares per Year"),
        validators=[MinValueValidator(0), MaxValueValidator(2)],
        choices=FlareFreqs.choices,
        help_text="How many gout flares does the patient have per year?",
        blank=True,
        null=True,
    )
    indication = IntegerField(
        _("Indication"),
        validators=[MinValueValidator(0), MaxValueValidator(2)],
        choices=Indications.choices,
        help_text="Does the patient have an indication for ULT?",
        default=Indications.NOTINDICATED,
    )
    num_flares = IntegerField(
        _("Total Number of Flares"),
        choices=FlareNums.choices,
        validators=[MinValueValidator(0), MaxValueValidator(2)],
        help_text="How many gout flares has the patient had?",
    )
    patient = OneToOneField(User, on_delete=CASCADE, editable=False)
    history = HistoricalRecords()
