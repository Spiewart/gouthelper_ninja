from ninja import Schema

from gouthelper_ninja.utils.schema import PatientIdSchema


class MedHistoryEditSchema(Schema):
    history_of: bool


class CkdEditSchema(MedHistoryEditSchema):
    pass


class GoutEditSchema(MedHistoryEditSchema):
    pass


class MedHistorySchema(MedHistoryEditSchema, PatientIdSchema):
    class Config:
        json_schema_extra = {
            "example": {
                "mhtype": "diabetes",
                "patient_id": "patient_id",
                "id": "medhistory_id",
            },
        }
