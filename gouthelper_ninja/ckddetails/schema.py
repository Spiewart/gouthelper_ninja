from decimal import Decimal
from typing import Self

from ninja import Schema
from pydantic import Field
from pydantic import computed_field
from pydantic import model_validator

from gouthelper_ninja.ckddetails.choices import DialysisChoices
from gouthelper_ninja.ckddetails.choices import DialysisDurations
from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.labs.helpers import egfr_calculator
from gouthelper_ninja.labs.helpers import stage_calculator
from gouthelper_ninja.utils.schema import PatientIdSchema


class CkdDetailEditSchema(Schema):
    dialysis: bool = False
    dialysis_duration: DialysisDurations | None = None
    dialysis_type: DialysisChoices | None = None
    stage: Stages | None = None
    age: int | None = Field(
        default=None,
        description=(
            "Age of the patient in years. "
            "Only required if the stage needs to be calculated.",
        ),
        ge=0,
        le=120,
    )
    creatinine: Decimal | None = Field(
        default=None,
        description=(
            "Serum creatinine level in mg/dL. "
            "Only required if the stage needs to be calculated.",
        ),
        max_digits=4,
        decimal_places=2,
        ge=0.10,
        le=20.00,
    )
    gender: Genders | None = None

    @computed_field
    @property
    def calculated_stage(self) -> Stages | None:
        """Stage calculated based on age, creatinine, and gender. Returns None
        if the stage cannot be calculated."""
        if self.age and self.creatinine and self.gender is not None:
            return stage_calculator(
                egfr_calculator(
                    creatinine=self.creatinine,
                    age=self.age,
                    gender=self.gender,
                ),
            )
        return None

    @model_validator(mode="after")
    def stage_dialysis_valid(self) -> Self:
        """Validates that stage and dialysis information make sense,
        i.e., if on dialysis, stage must be 5, or if not on dialysis,
        stage must be provided or calculated."""
        if self.dialysis and (self.stage or self.calculated_stage):
            msg = None
            if self.stage and self.stage != Stages.FIVE:
                msg = f"Stage: {self.stage} is not compatible with dialysis."
            if self.calculated_stage and self.calculated_stage != Stages.FIVE:
                if msg:
                    msg += (
                        f" Calculated stage: {self.calculated_stage} is not "
                        "compatible with dialysis."
                    )
                else:
                    msg = (
                        f"Calculated stage: {self.calculated_stage} is not "
                        "compatible with dialysis."
                    )
            if msg:
                raise ValueError(msg)
        elif not self.dialysis and not self.stage and not self.calculated_stage:
            msg = (
                "If dialysis is False, either stage or demographic "
                "data and creatinine to calculate a stage must be provided.",
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def stage_same_as_calculated(self) -> Self:
        """If stage is provided, it must match the calculated stage."""
        if self.stage and self.calculated_stage:
            if self.stage != self.calculated_stage:
                msg = (
                    f"Provided stage: {self.stage} does not match "
                    f"calculated stage: {self.calculated_stage}.",
                )
                raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def dialysis_info_valid(self) -> Self:
        """If dialysis is True, dialysis_duration and dialysis_type must be set."""
        if self.dialysis:
            if not self.dialysis_duration or not self.dialysis_type:
                msg = (
                    "If dialysis is True, both dialysis_duration and "
                    "dialysis_type must be provided.",
                )
                raise ValueError(msg)
        return self


class CkdDetailSchema(PatientIdSchema, CkdDetailEditSchema):
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "patient_id",
                "id": "gout_detail_id",
                "stage": 3,
                "dialysis": False,
                "dialysis_duration": "nan",
                "dialysis_type": "nan",
            },
        }
