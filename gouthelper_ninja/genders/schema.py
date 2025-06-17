from ninja import Schema

from gouthelper_ninja.genders.choices import Genders


class GenderEditSchema(Schema):
    gender: Genders


class GenderSchema(GenderEditSchema):
    id: str  # Assuming id is a string, typically a UUID or similar identifier
    patient: str  # Assuming patient is a string, typically a UUID or similar identifier

    class Config:
        schema_extra = {
            "example": {
                "gender": "male",
                "patient": "patient_id",
                "id": "gender_id",
            },
        }
