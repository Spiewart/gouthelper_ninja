from uuid import UUID

from ninja import Schema

from gouthelper_ninja.genders.choices import Genders


class GenderEditSchema(Schema):
    gender: Genders


class GenderSchema(GenderEditSchema):
    patient_id: UUID
    id: UUID

    class Config:
        json_schema_extra = {
            "example": {
                "gender": "male",
                "patient": "patient_id",
                "id": "gender_id",
            },
        }
