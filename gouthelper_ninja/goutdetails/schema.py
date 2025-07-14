from ninja import Schema

from gouthelper_ninja.utils.schema import PatientIdSchema


class GoutDetailEditSchema(Schema):
    at_goal: bool | None = None
    at_goal_long_term: bool = False
    flaring: bool | None = None
    on_ppx: bool = False
    on_ult: bool = False
    starting_ult: bool = False


class GoutDetailSchema(PatientIdSchema, GoutDetailEditSchema):
    class Config:
        json_schema_extra = {
            "example": {
                "at_goal": True,
                "at_goal_long_term": False,
                "flaring": False,
                "on_ppx": True,
                "on_ult": False,
                "starting_ult": False,
                "patient_id": "patient_id",
                "id": "gout_detail_id",
            },
        }
