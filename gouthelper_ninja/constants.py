from decimal import Decimal
from enum import Enum

# TODO: put this in some sort of User settings model
MIN_MENOPAUSE_AGE = 40
MAX_MENOPAUSE_AGE = 60


class CkdEgfrCutoffs(Enum):
    ONE = 90
    TWO = 60
    THREE = 30
    FOUR = 15


class EgfrSexModifiers(Enum):
    MALE = Decimal("1.000")
    FEMALE = Decimal("1.012")


class EgfrAlphas(Enum):
    MALE = Decimal("-0.302")
    FEMALE = Decimal("-0.241")


class EgfrKappas(Enum):
    MALE = Decimal("0.9")
    FEMALE = Decimal("0.7")
