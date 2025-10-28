from gouthelper_ninja.ckddetails.schema import PatientCkdDetailEditSchema
from gouthelper_ninja.utils.schema import PatientEditSchema
from gouthelper_ninja.utils.schema import PatientIdSchema


class MedHistoryEditSchema(PatientEditSchema):
    history_of: bool


class MedHistorySchema(PatientIdSchema, MedHistoryEditSchema):
    class Config:
        json_schema_extra = {
            "example": {
                "patient": {
                    "id": "patient_id",
                },
                "id": "medhistory_id",
            },
        }


class CkdEditSchema(MedHistoryEditSchema):
    """Editing schema for chronic kidney disease (CKD) medical
    history, including details about the CKD and any baseline
    creatinine level for the patient."""

    patient: PatientCkdDetailEditSchema
