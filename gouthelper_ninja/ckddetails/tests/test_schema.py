from decimal import Decimal

import pytest
from pydantic import ValidationError

from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.ckddetails.schema import CkdDetailEditSchema
from gouthelper_ninja.ckddetails.tests.factories import CkdDetailFactory
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.labs.helpers import egfr_calculator
from gouthelper_ninja.labs.helpers import stage_calculator

pytestmark = pytest.mark.django_db


class TestCkdDetailEditSchema:
    def test_calculated_stage(self):
        # Test that a schema with enough data returns the correct calculated stage
        schema = CkdDetailEditSchema(
            age=50,
            creatinine=Decimal("1.0"),
            gender=Genders.MALE,
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
            age=None,
            creatinine=Decimal("1.0"),
            gender=Genders.MALE,
            stage=Stages.THREE,
        )
        assert schema.calculated_stage is None

    def test_stage_dialysis_valid(self):
        # Test that a schema with dialysis and stage 5 is valid
        schema = CkdDetailEditSchema(
            **CkdDetailFactory.stub(
                dialysis=True,
                stage=Stages.FIVE,
            ).__dict__,
        )
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
            age=50,
            creatinine=Decimal("1.0"),
            gender=Genders.MALE,
        )
        assert schema.stage_dialysis_valid() == schema
