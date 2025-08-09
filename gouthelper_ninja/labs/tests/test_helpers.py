from decimal import Decimal

from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.constants import CkdEgfrCutoffs
from gouthelper_ninja.constants import EgfrAlphas
from gouthelper_ninja.constants import EgfrKappas
from gouthelper_ninja.constants import EgfrSexModifiers
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.labs.helpers import egfr_calculator
from gouthelper_ninja.labs.helpers import get_sex_modifier_alpha_kappa
from gouthelper_ninja.labs.helpers import stage_calculator


class TestEgfrCalculator:
    def test_returns_correct_value(self):
        # Test valid eGFR calculation for male
        egfr = egfr_calculator(Decimal("1.2"), 45, Genders.MALE)
        assert egfr == Decimal("76")

        # Test valid eGFR calculation for female
        egfr = egfr_calculator(Decimal("1.2"), 45, Genders.FEMALE)
        assert egfr == Decimal("57")

        # Test valid eGFR calculation for edge cases
        egfr = egfr_calculator(Decimal("0.8"), 30, Genders.MALE)
        assert egfr == Decimal("122")

        egfr = egfr_calculator(Decimal("0.8"), 30, Genders.FEMALE)
        assert egfr == Decimal("102")

    def test__returns_correct_type(self):
        # Test that the function returns a Decimal type
        egfr = egfr_calculator(Decimal("1.2"), 45, Genders.MALE)
        assert isinstance(egfr, Decimal)

    def test__returns_correct_decimal_places(self):
        # Test that the function returns a value rounded to 0 decimal places
        egfr = egfr_calculator(Decimal("1.2"), 45, Genders.MALE)
        assert egfr == Decimal("76")

        egfr = egfr_calculator(Decimal("1.2"), 45, Genders.FEMALE)
        assert egfr == Decimal("57")


class TestGetSexModifierAlphaKappa:
    def test_get_sex_modifier_alpha_kappa(self):
        # Test male constants
        sex_modifier, alpha, kappa = get_sex_modifier_alpha_kappa(Genders.MALE)
        assert sex_modifier == EgfrSexModifiers.MALE.value
        assert alpha == EgfrAlphas.MALE.value
        assert kappa == EgfrKappas.MALE.value

        # Test female constants
        sex_modifier, alpha, kappa = get_sex_modifier_alpha_kappa(Genders.FEMALE)
        assert sex_modifier == EgfrSexModifiers.FEMALE.value
        assert alpha == EgfrAlphas.FEMALE.value
        assert kappa == EgfrKappas.FEMALE.value


class TestStageCalculator:
    def test_stage_calculator(self):
        # Test valid CKD stages
        assert stage_calculator(Decimal("90")) == Stages.ONE
        assert stage_calculator(Decimal("60")) == Stages.TWO
        assert stage_calculator(Decimal("45")) == Stages.THREE
        assert stage_calculator(Decimal("30")) == Stages.THREE
        assert stage_calculator(Decimal("15")) == Stages.FOUR
        assert stage_calculator(Decimal("5")) == Stages.FIVE

        # Test edge cases
        assert stage_calculator(CkdEgfrCutoffs.ONE.value) == Stages.ONE
        assert stage_calculator(CkdEgfrCutoffs.TWO.value) == Stages.TWO
        assert stage_calculator(CkdEgfrCutoffs.THREE.value) == Stages.THREE
        assert stage_calculator(CkdEgfrCutoffs.FOUR.value) == Stages.FOUR
