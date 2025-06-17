from datetime import date
from uuid import UUID

from ninja import Schema


class DateOfBirthEditSchema(Schema):
    dateofbirth: date


class DateOfBirthSchema(DateOfBirthEditSchema):
    id: UUID
    patient_id: UUID

    class Config:
        schema_extra = {
            "example": {
                "dateofbirth": "2000-01-01",
                "patient_id": "patient_id",
                "id": "dateofbirth_id",
            },
        }
