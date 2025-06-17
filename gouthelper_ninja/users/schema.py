from uuid import UUID

from ninja import Schema
from pydantic import ConfigDict

from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.ethnicitys.schema import EthnicityEditSchema
from gouthelper_ninja.genders.schema import GenderEditSchema
from gouthelper_ninja.utils.schema import IdSchema


class PatientBaseSchema(
    Schema,
):
    dateofbirth: DateOfBirthEditSchema
    ethnicity: EthnicityEditSchema
    gender: GenderEditSchema

    model_config = ConfigDict(
        extra="forbid",
    )


class PatientSchema(PatientBaseSchema, IdSchema):
    pass


class PatientEditSchema(
    PatientBaseSchema,
):
    pass


class ProviderPatientCreateSchema(
    PatientEditSchema,
):
    provider_id: UUID
