from datetime import date

from ninja import Schema

from gouthelper_ninja.utils.schema import PatientIdSchema


class DateOfBirthEditSchema(Schema):
    dateofbirth: date


class DateOfBirthSchema(DateOfBirthEditSchema, PatientIdSchema):
    class Config:
        json_schema_extra = {
            "example": {
                "dateofbirth": "2000-01-01",
                "patient_id": "patient_id",
                "id": "dateofbirth_id",
            },
        }
