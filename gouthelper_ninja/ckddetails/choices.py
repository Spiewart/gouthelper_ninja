from django.db.models import IntegerChoices
from django.utils.translation import gettext_lazy as _


class DialysisChoices(IntegerChoices):
    HEMODIALYSIS = 1, _("Hemodialysis")
    PERITONEAL = 2, _("Peritoneal Dialysis")


class DialysisDurations(IntegerChoices):
    LESSTHANSIX = 1, _("Less than six months")
    LESSTHANYEAR = 2, _("Between six months and a year")
    MORETHANYEAR = 3, _("More than a year")


class Stages(IntegerChoices):
    ONE = 1, _("I")
    TWO = 2, _("II")
    THREE = 3, _("III")
    FOUR = 4, _("IV")
    FIVE = 5, _("V")
    __empty__ = _("----")
