from ninja import Schema

from gouthelper_ninja.dateofbirths.schema import DateOfBirthNestedSchema
from gouthelper_ninja.ethnicitys.schema import EthnicityNestedSchema
from gouthelper_ninja.genders.schema import GenderNestedSchema


class PatientUpdateSchema(
    DateOfBirthNestedSchema,
    EthnicityNestedSchema,
    GenderNestedSchema,
):
    pass


class PatientCreateSchema(
    PatientUpdateSchema,
):
    provider: str | None = None


class PatientSchema(Schema):
    id: str
    username: str
    email: str | None = None
