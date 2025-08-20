from decimal import Decimal
from typing import Any

from ninja import Schema
from pydantic import Field
from pydantic import model_serializer

from gouthelper_ninja.labs.choices import CreatinineLimits
from gouthelper_ninja.labs.choices import Units
from gouthelper_ninja.utils.schema import PatientIdSchema


class BaselineCreatinineEditSchema(Schema):
    """Schema for editing BaselineCreatinine instances."""

    lower_limit: CreatinineLimits = CreatinineLimits.LOWERMGDL
    units: Units = Units.MGDL
    upper_limit: CreatinineLimits = CreatinineLimits.UPPERMGDL
    value: Decimal = Field(
        description="Baseline creatinine value in mg/dL",
        max_digits=4,
        decimal_places=2,
        ge=0.50,
        le=5.00,
    )

    @model_serializer
    def serialize_baseline_creatinine(self) -> dict[str, Any]:
        """Returns only the fields relevant for editing a
        BaselineCreatinine instance."""
        return {
            "value": self.value,
        }


class BaselineCreatinineSchema(PatientIdSchema, BaselineCreatinineEditSchema):
    """Schema for BaselineCreatinine instances with patient_id."""

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "patient_id",
                "id": "baseline_creatinine_id",
                "value": 1.20,
            },
        }

    @model_serializer
    def serialize_baseline_creatinine(self) -> dict[str, Any]:
        """Returns all fields for serialization of a
        BaselineCreatinine instance."""
        serialized = super().serialize_baseline_creatinine()
        return {
            **serialized,
            "id": str(self.id),
            "patient_id": str(self.patient_id),
        }
