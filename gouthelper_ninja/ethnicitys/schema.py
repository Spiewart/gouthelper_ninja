from ninja import Schema

from gouthelper_ninja.ethnicitys.choices import Ethnicitys


class EthnicityEditSchema(Schema):
    ethnicity: Ethnicitys


class EthnicitySchema(EthnicityEditSchema):
    patient: str
    id: str

    class Config:
        json_schema_extra = {
            "example": {
                "ethnicitypatient": "patient_id",
                "id": "ethnicity_id",
            },
        }
