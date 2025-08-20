from decimal import Decimal

from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.constants import CkdEgfrCutoffs
from gouthelper_ninja.constants import EgfrAlphas
from gouthelper_ninja.constants import EgfrKappas
from gouthelper_ninja.constants import EgfrSexModifiers
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.labs.helpers import BaselineCreatinineCalc
from gouthelper_ninja.labs.helpers import egfr_calculator
from gouthelper_ninja.labs.helpers import egfr_range_for_stage
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


class TestEgfrRangeForStage:
    def test_egfr_range_for_stage_returns_correct_ranges(self):
        # Test each CKD stage returns correct eGFR range
        assert egfr_range_for_stage(Stages.ONE) == (90, 120)
        assert egfr_range_for_stage(Stages.TWO) == (60, 89)
        assert egfr_range_for_stage(Stages.THREE) == (30, 59)
        assert egfr_range_for_stage(Stages.FOUR) == (15, 29)
        assert egfr_range_for_stage(Stages.FIVE) == (0, 14)

    def test_egfr_range_for_stage_returns_tuple(self):
        # Test that function returns a tuple
        result = egfr_range_for_stage(Stages.ONE)
        assert isinstance(result, tuple)
        expected_tuple_len = 2
        assert len(result) == expected_tuple_len

    def test_egfr_range_for_stage_returns_integers(self):
        # Test that function returns integer values
        min_egfr, max_egfr = egfr_range_for_stage(Stages.TWO)
        assert isinstance(min_egfr, int)
        assert isinstance(max_egfr, int)


class TestBaselineCreatinineCalc:
    def test_baseline_creatinine_calc_initialization(self):
        # Test that the class initializes correctly
        calc = BaselineCreatinineCalc(Stages.THREE, 45, Genders.MALE)
        assert calc.stage == Stages.THREE
        expected_age = 45
        assert calc.age == expected_age
        assert calc.gender == Genders.MALE
        expected_min_egfr = 30
        expected_max_egfr = 59
        assert calc.min_egfr == expected_min_egfr
        assert calc.max_egfr == expected_max_egfr
        assert isinstance(calc.creat, Decimal)

    def test_baseline_creatinine_calc_sets_egfr_range(self):
        # Test that min_egfr and max_egfr are set from egfr_range_for_stage
        calc = BaselineCreatinineCalc(Stages.TWO, 50, Genders.FEMALE)
        expected_min_egfr = 60
        expected_max_egfr = 89
        assert calc.min_egfr == expected_min_egfr
        assert calc.max_egfr == expected_max_egfr

        calc = BaselineCreatinineCalc(Stages.FOUR, 70, Genders.MALE)
        expected_min_egfr = 15
        expected_max_egfr = 29
        assert calc.min_egfr == expected_min_egfr
        assert calc.max_egfr == expected_max_egfr

    def test_baseline_creatinine_calc_calculate_returns_decimal(self):
        # Test that calculate method returns a Decimal
        calc = BaselineCreatinineCalc(Stages.THREE, 45, Genders.MALE)
        result = calc.calculate()
        assert isinstance(result, Decimal)

    def test_baseline_creatinine_calc_calculate_returns_valid_range(self):
        # Test that calculated creatinine produces eGFR in correct range
        calc = BaselineCreatinineCalc(Stages.TWO, 50, Genders.FEMALE)
        result = calc.calculate()

        # Calculate eGFR for the returned creatinine
        calculated_egfr = egfr_calculator(result, 50, Genders.FEMALE)

        # Should be within the range for stage 2 (60-89)
        assert CkdEgfrCutoffs.TWO.value <= calculated_egfr < CkdEgfrCutoffs.ONE.value

    def test_baseline_creatinine_calc_calculate_precision(self):
        # Test that calculate method returns value rounded to 2 decimal places
        calc = BaselineCreatinineCalc(Stages.ONE, 30, Genders.MALE)
        result = calc.calculate()

        # Check that it has at most 2 decimal places
        expected_exponent = -2
        assert result.as_tuple().exponent >= expected_exponent

    def test_baseline_creatinine_calc_multiple_stages(self):
        # Test calculation works for all CKD stages
        for stage in [Stages.ONE, Stages.TWO, Stages.THREE, Stages.FOUR, Stages.FIVE]:
            calc = BaselineCreatinineCalc(stage, 45, Genders.MALE)
            result = calc.calculate()
            assert isinstance(result, Decimal)
            assert result > 0

    def test_baseline_creatinine_calc_different_demographics(self):
        # Test calculation works for different age/gender combinations
        demographics = [
            (25, Genders.MALE),
            (45, Genders.FEMALE),
            (65, Genders.MALE),
            (80, Genders.FEMALE),
        ]

        for age, gender in demographics:
            calc = BaselineCreatinineCalc(Stages.THREE, age, gender)
            result = calc.calculate()
            assert isinstance(result, Decimal)
            assert result > 0
