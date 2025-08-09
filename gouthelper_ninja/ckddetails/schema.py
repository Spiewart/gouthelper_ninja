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
from gouthelper_ninja.utils.schema import PatientIdSchema


class CkdDetailEditSchema(Schema):
    dialysis: bool = False
    dialysis_duration: DialysisDurations | None = None
    dialysis_type: DialysisChoices | None = None
    stage: Stages | None = None
    age: int = Field(
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
    def calculated_stage(self) -> Stages:
        """Stage calculated based on age, creatinine, and gender."""


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

    @model_validator(mode="after")
    def check_stage_dialysis_valid(self) -> Self:
        if self.password != self.password_repeat:
            msg = "Passwords do not match"
            raise ValueError(msg)
        return self
