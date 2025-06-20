from uuid import UUID

from ninja import Schema

from gouthelper_ninja.ethnicitys.choices import Ethnicitys


class EthnicityEditSchema(Schema):
    ethnicity: Ethnicitys


class EthnicitySchema(EthnicityEditSchema):
    patient_id: UUID
    id: UUID

    class Config:
        json_schema_extra = {
            "example": {
                "ethnicity": "AFRICANAMERICAN",
                "patient_id": "patient_id",
                "id": "ethnicity_id",
            },
        }
