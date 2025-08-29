from decimal import Decimal

import pytest
from pydantic import ValidationError

from gouthelper_ninja.ckddetails.choices import DialysisChoices
from gouthelper_ninja.ckddetails.choices import DialysisDurations
from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.ckddetails.schema import CkdDetailEditSchema
from gouthelper_ninja.ckddetails.tests.factories import CkdDetailFactory
from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.schema import GenderEditSchema
from gouthelper_ninja.labs.helpers import egfr_calculator
from gouthelper_ninja.labs.helpers import stage_calculator
from gouthelper_ninja.labs.schema import BaselineCreatinineEditSchema
from gouthelper_ninja.utils.helpers import dateofbirth_calc

pytestmark = pytest.mark.django_db


class TestCkdDetailEditSchema:
    def test_calculated_stage(self):
        # Test that a schema with enough data returns the correct calculated stage
        schema = CkdDetailEditSchema(
            dateofbirth=(
                DateOfBirthEditSchema(
                    dateofbirth=dateofbirth_calc(50),
                )
            ),
            baselinecreatinine=(BaselineCreatinineEditSchema(value=Decimal("1.0"))),
            gender=GenderEditSchema(gender=Genders.MALE),
        )
        assert schema.calculated_stage == stage_calculator(
            egfr_calculator(
                creatinine=Decimal("1.0"),
                age=50,
                gender=Genders.MALE,
            ),
        )
        # Test that a schema without enough data returns None
        schema = CkdDetailEditSchema(
            dateofbirth=None,
            baselinecreatinine=(BaselineCreatinineEditSchema(value=Decimal("1.0"))),
            gender=GenderEditSchema(gender=Genders.MALE),
            stage=Stages.THREE,
        )
        assert schema.calculated_stage is None

    def test__serializer_ckddetail(self):
        # Schema with dialysis returns stage 5
        schema = CkdDetailEditSchema(
            dialysis=True,
            dialysis_duration=DialysisDurations.LESSTHANSIX,
            dialysis_type=DialysisChoices.HEMODIALYSIS,
            stage=None,
        )
        serialized = schema.model_dump()
        assert serialized["stage"] == Stages.FIVE
        assert serialized["dialysis"] is True
        assert serialized["dialysis_duration"] == DialysisDurations.LESSTHANSIX
        assert serialized["dialysis_type"] == DialysisChoices.HEMODIALYSIS

        # Schema with a calculated stage but no stage or dialysis
        # returns calculated stage
        schema = CkdDetailEditSchema(
            dateofbirth=(
                DateOfBirthEditSchema(
                    dateofbirth=dateofbirth_calc(50),
                )
            ),
            baselinecreatinine=(BaselineCreatinineEditSchema(value=Decimal("1.0"))),
            gender=GenderEditSchema(gender=Genders.MALE),
            stage=None,
            dialysis=False,
        )
        serialized = schema.model_dump()
        assert serialized["stage"] == schema.calculated_stage
        assert serialized["dialysis"] is False
        assert serialized["dialysis_duration"] is None
        assert serialized["dialysis_type"] is None

        # Schema with a stage and no dialysis returns stage
        schema = CkdDetailEditSchema(
            stage=Stages.FOUR,
            dialysis=False,
        )
        serialized = schema.model_dump()
        assert serialized["stage"] == Stages.FOUR
        assert serialized["dialysis"] is False
        assert serialized["dialysis_duration"] is None
        assert serialized["dialysis_type"] is None

    def test_stage_dialysis_valid(self):
        ckddetail_kwargs = CkdDetailFactory.stub(
            dialysis=True,
            stage=Stages.FIVE,
        ).__dict__

        # Test that a schema with dialysis and stage 5 is valid
        schema = CkdDetailEditSchema(**ckddetail_kwargs)
        assert schema.stage_dialysis_valid() == schema

        # Test that a schema with dialysis and stage not 5 raises
        # ValidationError
        with pytest.raises(ValidationError) as exc:
            CkdDetailEditSchema(
                dialysis=True,
                stage=Stages.THREE,
            )
        assert f"Stage: {Stages.THREE} is not compatible with dialysis." in str(
            exc.value,
        )

        # Test that a schema without dialysis but with enough data to
        # calculate stage is valid
        schema = CkdDetailEditSchema(
            dateofbirth=(
                DateOfBirthEditSchema(
                    dateofbirth=dateofbirth_calc(50),
                )
            ),
            baselinecreatinine=(BaselineCreatinineEditSchema(value=Decimal("1.0"))),
            gender=GenderEditSchema(gender=Genders.MALE),
        )
        assert schema.stage_dialysis_valid() == schema

        # Test that a schema without dialysis and no stage or calculated
        # stage raises ValidationError
        ckddetail_kwargs.update(
            dialysis=False,
            dateofbirth=None,
            stage=None,
            # Set dialysis_duration and dialysis_type to None
            # Avoids ValidationError from field validators
            dialysis_duration=None,
            dialysis_type=None,
        )
        with pytest.raises(ValidationError) as exc:
            CkdDetailEditSchema(**ckddetail_kwargs)
        assert (
            "If dialysis is False, either stage or demographic data and "
            "creatinine to calculate a stage must be provided." in str(exc.value)
        )

    def test_stage_same_as_calculated(self):
        # Test that a schema with stage and calculated stage being the
        # same is valid
        schema = CkdDetailEditSchema(
            dateofbirth=DateOfBirthEditSchema(
                dateofbirth=dateofbirth_calc(50),
            ),
            baselinecreatinine=(BaselineCreatinineEditSchema(value=Decimal("2.0"))),
            gender=GenderEditSchema(gender=Genders.MALE),
            stage=Stages.THREE,
        )
        assert schema.stage_same_as_calculated() == schema
        # Test that a schema with stage and calculated stage being different
        # raises ValidationError
        with pytest.raises(ValidationError) as exc:
            CkdDetailEditSchema(
                dateofbirth=DateOfBirthEditSchema(
                    dateofbirth=dateofbirth_calc(50),
                ),
                baselinecreatinine=(BaselineCreatinineEditSchema(value=Decimal("1.0"))),
                gender=GenderEditSchema(gender=Genders.MALE),
                stage=Stages.THREE,
            )
        assert (
            f"Provided stage: {Stages.THREE} does not match "
            f"calculated stage: {Stages.ONE}."
        ) in str(
            exc.value,
        )

    def test__validate_dialysis_duration(self):
        # Test that a schema with dialysis set to True and dialysis_duration
        # set
        assert CkdDetailEditSchema(
            dialysis=True,
            dialysis_duration=DialysisDurations.LESSTHANSIX,
        )

        # Test that a schema with dialysis set to True and no dialysis_duration
        # raises
        with pytest.raises(ValidationError) as exc:
            CkdDetailEditSchema(dialysis=True, dialysis_duration=None)
        assert "dialysis_duration must be provided if dialysis is True." in str(
            exc.value,
        )

        # Test that a schema with dialysis set to False and dialysis_duration
        # set raises
        with pytest.raises(ValidationError) as exc:
            CkdDetailEditSchema(
                dialysis=False,
                dialysis_duration=DialysisDurations.LESSTHANSIX,
            )
        assert "dialysis_duration should not be set if dialysis is False." in str(
            exc.value,
        )

    def test__validate_dialysis_type(self):
        # Test that a schema with dialysis set to True and dialysis_type set
        assert CkdDetailEditSchema(
            dialysis=True,
            dialysis_type=DialysisChoices.HEMODIALYSIS,
        )

        # Test that a schema with dialysis set to True and no dialysis_type
        # raises
        with pytest.raises(ValidationError) as exc:
            CkdDetailEditSchema(dialysis=True, dialysis_type=None)
        assert "dialysis_type must be provided if dialysis is True." in str(exc.value)

        # Test that a schema with dialysis set to False and dialysis_type set
        # raises
        with pytest.raises(ValidationError) as exc:
            CkdDetailEditSchema(
                dialysis=False,
                dialysis_type=DialysisChoices.HEMODIALYSIS,
            )
        assert "dialysis_type should not be set if dialysis is False." in str(exc.value)

    def test__validate_stage(self):
        # Schema with a stage is valid
        assert CkdDetailEditSchema(stage=Stages.THREE)

        # Schema without a stage but with dialysis=True is valid
        valid_ckddetail = CkdDetailEditSchema(
            dialysis=True,
            dialysis_duration=DialysisDurations.LESSTHANSIX,
            dialysis_type=DialysisChoices.HEMODIALYSIS,
            stage=None,
        )
        # If dialysis is True and no stage is provided, stage is set to 5
        assert valid_ckddetail.stage == Stages.FIVE
