import random
from decimal import Decimal

from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.constants import CkdEgfrCutoffs
from gouthelper_ninja.constants import EgfrAlphas
from gouthelper_ninja.constants import EgfrKappas
from gouthelper_ninja.constants import EgfrSexModifiers
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.utils.helpers import round_decimal


class BaselineCreatinineCalc:
    """Class method to calculate a range of baseline creatinine values
    for a given CKD stage, age, and gender."""

    def __init__(
        self,
        stage: Stages,
        age: int,
        gender: Genders,
    ):
        self.stage = stage
        self.age = age
        self.gender = gender
        self.min_egfr, self.max_egfr = egfr_range_for_stage(stage)
        self.creat = Decimal(random.uniform(0, 5))  # noqa: S311

    def calculate(self) -> Decimal:
        """Method that recursively derives a baseline creatinine value for the
        given CKD stage and patient age and gender."""
        egfr = egfr_calculator(self.creat, self.age, self.gender)
        while egfr < self.min_egfr or egfr > self.max_egfr:
            if egfr < self.min_egfr:
                self.creat = Decimal(
                    random.uniform(0, float(self.creat)),  # noqa: S311
                )
                return self.calculate()
            self.creat = Decimal(
                random.uniform(float(self.creat), 5),  # noqa: S311
            )
            return self.calculate()
        return round_decimal(self.creat, 2)


def egfr_range_for_stage(
    stage: Stages,
) -> tuple[int, int]:
    """Method that takes a CKD stage and returns a tuple of the
    low and high eGFR bounds for that stage."""
    if stage == Stages.ONE:
        return 90, 120
    if stage == Stages.TWO:
        return 60, 89
    if stage == Stages.THREE:
        return 30, 59
    if stage == Stages.FOUR:
        return 15, 29
    return 0, 14


def egfr_calculator(
    creatinine: Decimal,  # TODO: creatinine can be Creatinine when implemented
    age: int,
    gender: Genders,
) -> Decimal:
    """
    Calculates eGFR from Creatinine value.
    Need to know age and gender.
    https://www.kidney.org/professionals/kdoqi/gfr_calculator/formula

    args:
        creatinine: Decimal value
        age (int): age of patient in years
        gender (Genders enum = int): Genders (MALE or FEMALE)

    returns: eGFR (decimal) rounded to 0 decimal points
    """

    # Set gender-based variables for CKD-EPI Creatinine Equation
    sex_modifier, alpha, kappa = get_sex_modifier_alpha_kappa(
        gender,
    )
    # Calculate eGFR
    egfr = (
        Decimal(142)
        * min(creatinine / kappa, Decimal("1.00")) ** alpha
        * max(creatinine / kappa, Decimal("1.00")) ** Decimal("-1.200")
        * Decimal("0.9938") ** age
        * sex_modifier
    )
    # Return eGFR rounded to 0 decimal points
    return round_decimal(egfr, 0)


def get_sex_modifier_alpha_kappa(
    gender: Genders,
) -> tuple[
    Decimal,
    Decimal,
    Decimal,
]:
    """
    Returns tuple of sex_modifier, alpha, and kappa sex-based
    constants for eGFR calculation.
    """
    return (
        (
            EgfrSexModifiers.MALE.value,
            EgfrAlphas.MALE.value,
            EgfrKappas.MALE.value,
        )
        if gender == Genders.MALE
        else (
            EgfrSexModifiers.FEMALE.value,
            EgfrAlphas.FEMALE.value,
            EgfrKappas.FEMALE.value,
        )
    )


def stage_calculator(egfr: Decimal) -> Stages:
    """Method that calculates CKD stage from an eGFR.

    Args:
        egfr (decimal): eGFR value

    Returns:
        Stages enum object: CKD stage
    """
    # Use eGFR to determine CKD stage and return
    return (
        Stages.ONE
        if egfr >= CkdEgfrCutoffs.ONE.value
        else Stages.TWO
        if CkdEgfrCutoffs.ONE.value > egfr >= CkdEgfrCutoffs.TWO.value
        else Stages.THREE
        if CkdEgfrCutoffs.TWO.value > egfr >= CkdEgfrCutoffs.THREE.value
        else Stages.FOUR
        if CkdEgfrCutoffs.THREE.value > egfr >= CkdEgfrCutoffs.FOUR.value
        else Stages.FIVE
    )
