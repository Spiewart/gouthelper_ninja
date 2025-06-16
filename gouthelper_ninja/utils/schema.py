from uuid import UUID

from ninja import Schema


class IdSchema(Schema):
    id: UUID
