from ninja import Schema

from gouthelper_ninja.dateofbirths.schema import DateOfBirthNestedSchema
from gouthelper_ninja.ethnicitys.schema import EthnicityNestedSchema
from gouthelper_ninja.genders.schema import GenderNestedSchema


class PatientCreateSchema(
    DateOfBirthNestedSchema,
    EthnicityNestedSchema,
    GenderNestedSchema,
):
    provider: str | None = None


class PatientUpdateSchema(
    DateOfBirthNestedSchema,
    EthnicityNestedSchema,
    GenderNestedSchema,
):
    pass


class PatientSchema(Schema):
    id: str
    username: str
    email: str | None = None
