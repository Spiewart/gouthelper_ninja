from typing import Any
from typing import Self

from ninja import Schema
from pydantic import computed_field
from pydantic import field_validator
from pydantic import model_serializer
from pydantic import model_validator

from gouthelper_ninja.ckddetails.choices import DialysisChoices
from gouthelper_ninja.ckddetails.choices import DialysisDurations
from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.genders.schema import GenderEditSchema
from gouthelper_ninja.labs.helpers import egfr_calculator
from gouthelper_ninja.labs.helpers import stage_calculator
from gouthelper_ninja.labs.schema import BaselineCreatinineEditSchema
from gouthelper_ninja.utils.schema import PatientIdSchema


class CkdDetailEditSchema(Schema):
    """Schema for editing CkdDetail instances. Includes dateofbirth,
    gender, and baseline creatinine schema, which are not part of the
    CkdDetail model but are required to edit or create a CkdDetail."""

    dialysis: bool = False
    dialysis_duration: DialysisDurations | None = None
    dialysis_type: DialysisChoices | None = None
    dateofbirth: DateOfBirthEditSchema | None = None
    baselinecreatinine: BaselineCreatinineEditSchema | None = None
    gender: GenderEditSchema | None = None
    stage: Stages | None = None

    # There shouldn't be any dialysis_duration info if not on dialysis
    @field_validator("dialysis_duration", mode="after")
    @classmethod
    def validate_dialysis_duration(cls, value, info):
        """Ensure that dialysis_duration is only set if dialysis is True."""
        if value is None and info.data.get("dialysis"):
            msg = "dialysis_duration must be provided if dialysis is True."

            raise ValueError(
                msg,
            )
        if value is not None and not info.data.get("dialysis"):
            msg = "dialysis_duration should not be set if dialysis is False."
            raise ValueError(
                msg,
            )
        return value

    # There shouldn't be a dialysis_type info if not on dialysis
    @field_validator("dialysis_type", mode="after")
    @classmethod
    def validate_dialysis_type(cls, value, info):
        """Ensure that dialysis_type is only set if dialysis is True."""
        if value is None and info.data.get("dialysis"):
            # If dialysis is True, dialysis_type must be provided
            msg = "dialysis_type must be provided if dialysis is True."
            raise ValueError(
                msg,
            )
        if value is not None and not info.data.get("dialysis"):
            # If dialysis is False, dialysis_type should not be set
            msg = "dialysis_type should not be set if dialysis is False."
            raise ValueError(
                msg,
            )
        return value

    @computed_field
    @property
    def calculated_stage(self) -> Stages | None:
        """Stage calculated based on age, creatinine, and gender. Returns None
        if the stage cannot be calculated."""
        # Need nested schema values: dateofbirth.age, baselinecreatinine.value,
        # and gender.gender (GenderEditSchema stores the enum in `gender`).
        if (
            self.dateofbirth
            and self.baselinecreatinine
            and getattr(self.baselinecreatinine, "value", None) is not None
            and self.gender is not None
            and getattr(self.gender, "gender", None) is not None
        ):
            return stage_calculator(
                egfr_calculator(
                    creatinine=self.baselinecreatinine.value,
                    age=self.dateofbirth.age,
                    gender=self.gender.gender,
                ),
            )
        return None

    @field_validator("stage", mode="after")
    @classmethod
    def validate_stage(cls, value, info):
        """If dialysis is True and stage is not provided, set stage to 5."""
        if info.data.get("dialysis") and value is None:
            return Stages.FIVE
        return value

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

    @model_serializer
    def serialize_ckddetail(self) -> dict[str, Any]:
        """Returns only the fields relevant for editing a
        CkdDetail instance."""

        return {
            "dialysis": self.dialysis,
            "dialysis_duration": self.dialysis_duration,
            "dialysis_type": self.dialysis_type,
            "stage": (
                Stages.FIVE
                if self.dialysis
                else self.stage
                if self.stage
                else self.calculated_stage
            ),
        }


class CkdDetailSchema(PatientIdSchema, CkdDetailEditSchema):
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "patient_id",
                "id": "ckddetail_id",
                "dialysis": True,
                "dialysis_duration": DialysisDurations.MORETHANYEAR,
                "dialysis_type": DialysisChoices.HEMODIALYSIS,
                "stage": Stages.FIVE,
            },
        }

    @model_serializer
    def serialize_ckddetail(self) -> dict[str, Any]:
        """Returns all fields for serialization of a CkdDetail instance."""
        serialized = super().serialize_ckddetail()
        return {
            **serialized,
            "id": str(self.patient_id),
            "patient_id": str(self.patient_id),
        }
