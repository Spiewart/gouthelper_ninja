from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import CASCADE
from django.db.models import CharField
from django.db.models import CheckConstraint
from django.db.models import DecimalField
from django.db.models import Model
from django.db.models import OneToOneField
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from gouthelper_ninja.labs.choices import CreatinineLimits
from gouthelper_ninja.labs.choices import Units
from gouthelper_ninja.utils.helpers import get_user_change
from gouthelper_ninja.utils.models import GoutHelperModel

User = get_user_model()


class BaselineLab(
    GoutHelperModel,
    TimeStampedModel,
):
    patient = OneToOneField(User, on_delete=CASCADE, editable=False)
    history = HistoricalRecords(get_user=get_user_change, inherit=True)

    class Meta:
        abstract = True


class CreatinineBase(Model):
    CreatinineLimits = CreatinineLimits
    Units = Units

    lower_limit = DecimalField(
        max_digits=4,
        decimal_places=2,
        default=CreatinineLimits.LOWERMGDL,
    )
    units = CharField(
        _("Units"),
        choices=Units.choices,
        max_length=10,
        default=Units.MGDL,
    )
    upper_limit = DecimalField(
        max_digits=4,
        decimal_places=2,
        default=CreatinineLimits.UPPERMGDL,
    )
    value = DecimalField(
        max_digits=4,
        decimal_places=2,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"Creatinine: {self.value_str}"

    @property
    def value_str(self) -> str:
        return f"{self.value.quantize(Decimal('1.00'))} {self.get_units_display()}"


class BaselineCreatinine(CreatinineBase, BaselineLab):
    class Meta:
        constraints = [
            CheckConstraint(
                check=(
                    Q(lower_limit=CreatinineLimits.LOWERMGDL)
                    & Q(units=Units.MGDL)
                    & Q(upper_limit=CreatinineLimits.UPPERMGDL)
                ),
                name="%(class)s_units_limits_valid",
            ),
        ]

    def __str__(self):
        return f"Baseline {self.__str__()}"
