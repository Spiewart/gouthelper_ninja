from ninja import Schema

from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.utils.schema import PatientIdSchema


class GenderEditSchema(Schema):
    gender: Genders


class GenderSchema(PatientIdSchema, GenderEditSchema):
    class Config:
        json_schema_extra = {
            "example": {
                "gender": "male",
                "patient_id": "patient_id",
                "id": "gender_id",
            },
        }
