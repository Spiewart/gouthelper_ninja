from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.utils.schema import PatientEditSchema
from gouthelper_ninja.utils.schema import PatientIdSchema


class EthnicityEditSchema(PatientEditSchema):
    ethnicity: Ethnicitys


class EthnicitySchema(PatientIdSchema, EthnicityEditSchema):
    class Config:
        json_schema_extra = {
            "example": {
                "ethnicity": "AFRICANAMERICAN",
                "patient_id": "patient_id",
                "id": "ethnicity_id",
            },
        }
