from datetime import date

from ninja import Schema

from gouthelper_ninja.utils.helpers import age_calc
from gouthelper_ninja.utils.schema import PatientIdSchema


class DateOfBirthEditSchema(Schema):
    dateofbirth: date

    @property
    def age(self) -> int:
        return age_calc(self.dateofbirth)


class DateOfBirthSchema(DateOfBirthEditSchema, PatientIdSchema):
    class Config:
        json_schema_extra = {
            "example": {
                "dateofbirth": "2000-01-01",
                "patient_id": "patient_id",
                "id": "dateofbirth_id",
            },
        }
