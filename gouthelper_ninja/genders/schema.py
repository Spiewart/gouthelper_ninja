from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.utils.schema import PatientEditSchema
from gouthelper_ninja.utils.schema import PatientIdSchema


class GenderEditSchema(PatientEditSchema):
    gender: Genders


class GenderSchema(PatientIdSchema, GenderEditSchema):
    class Config:
        json_schema_extra = {
            "example": {
                "gender": "male",
                "patient": {
                    "id": "UUID",
                },
                "id": "gender_id",
            },
        }
