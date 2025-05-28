from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class Ethnicitys(TextChoices):
    AFRICANAMERICAN = "African American", _("African American")
    CAUCASIAN = "Caucasian", _("Caucasian")
    EASTAFRICAN = "East African", _("East African")
    HANCHINESE = "Han Chinese", _("Han Chinese")
    HISPANIC = "Hispanic", _("Hispanic")
    HMONG = "Hmong", _("Hmong")
    KOREAN = "Korean", _("Korean")
    NATIVEAMERICAN = "Native American", _("Native American")
    OTHER = "Other", _("Other")
    PACIFICISLANDER = "Pacific Islander", _("Pacific Islander")
    THAI = "Thai", _("Thai")
    PREFERNOTTOANSWER = "Prefer not to answer", _("Prefer not to answer")
