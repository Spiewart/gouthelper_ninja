from decimal import Decimal

from django.db.models import Choices
from django.db.models import IntegerChoices
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class Abnormalitys(IntegerChoices):
    LOW = 0, _("Low")
    HIGH = 1, _("High")


class LabLimits(Decimal, Choices):
    """Upper and lower limits for lab values.
    In the format {LOWER/UPPER}{UNIT}."""


class CreatinineLimits(LabLimits):
    LOWERMGDL = Decimal("0.74"), _("0.74 mg/dL")
    UPPERMGDL = Decimal("1.35"), _("1.35 mg/dL")


class UrateLimits(LabLimits):
    LOWERMGDL = Decimal("3.5"), _("3.5 mg/dL")
    UPPERMGDL = Decimal("7.2"), _("7.2 mg/dL")


class Units(TextChoices):
    """Units of reference choices for Labs."""

    MGDL = "MGDL", _("mg/dL (milligrams per deciliter)")
