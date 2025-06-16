from uuid import UUID

from ninja import Schema
from pydantic import ConfigDict

from gouthelper_ninja.dateofbirths.schema import DateOfBirthNestedSchema
from gouthelper_ninja.ethnicitys.schema import EthnicityNestedSchema
from gouthelper_ninja.genders.schema import GenderNestedSchema
from gouthelper_ninja.utils.schema import IdSchema


class PatientBaseSchema(
    Schema,
):
    dateofbirth: DateOfBirthNestedSchema
    ethnicity: EthnicityNestedSchema
    gender: GenderNestedSchema

    model_config = ConfigDict(
        extra="forbid",
    )

    # TODO: Could consider adding custom ValidationError to provide
    # TODO: more specific error messages for, for instance when provider_id
    # TODO: is sent to a non-provider endpoint.


class PatientSchema(PatientBaseSchema, IdSchema):
    pass


class PatientCreateSchema(
    PatientBaseSchema,
):
    pass


class ProviderPatientCreateSchema(
    PatientCreateSchema,
):
    provider_id: UUID
