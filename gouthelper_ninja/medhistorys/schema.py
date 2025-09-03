from ninja import Schema

from gouthelper_ninja.ckddetails.schema import CkdDetailEditSchema
from gouthelper_ninja.labs.schema import BaselineCreatinineEditSchema
from gouthelper_ninja.utils.schema import PatientIdSchema


class MedHistoryEditSchema(Schema):
    history_of: bool


class MedHistorySchema(MedHistoryEditSchema, PatientIdSchema):
    class Config:
        json_schema_extra = {
            "example": {
                "mhtype": "diabetes",
                "patient_id": "patient_id",
                "id": "medhistory_id",
            },
        }


class CkdEditSchema(MedHistoryEditSchema):
    """Editing schema for chronic kidney disease (CKD) medical
    history, including details about the CKD and any baseline
    creatinine level for the patient."""

    baselinecreatinine: BaselineCreatinineEditSchema | None
    ckddetail: CkdDetailEditSchema | None
