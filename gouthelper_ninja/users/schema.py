from ninja import Schema

from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.ethnicitys.schema import EthnicityEditSchema
from gouthelper_ninja.genders.schema import GenderEditSchema
from gouthelper_ninja.utils.schema import IdSchema


class PatientEditSchema(
    Schema,
):
    dateofbirth: DateOfBirthEditSchema
    ethnicity: EthnicityEditSchema
    gender: GenderEditSchema


class PatientSchema(PatientEditSchema, IdSchema):
    pass
