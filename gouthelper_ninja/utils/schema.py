from uuid import UUID

from ninja import Schema


class IdSchema(Schema):
    id: UUID


class OptionalIdSchema(Schema):
    id: UUID | None


class PatientEditSchema(Schema):
    patient: OptionalIdSchema


class PatientIdSchema(IdSchema):
    patient: IdSchema
