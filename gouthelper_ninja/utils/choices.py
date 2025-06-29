from django.db.models import IntegerChoices
from django.utils.translation import gettext_lazy as _


class Contraindications(IntegerChoices):
    ABSOLUTE = 0, _("Absolute")
    RELATIVE = 1, _("Relative")
    DOSEADJ = 2, _("Dose Adjustment Required")
