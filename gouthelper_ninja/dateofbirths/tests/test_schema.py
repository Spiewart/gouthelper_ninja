from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from gouthelper_ninja.dateofbirths.schema import DateOfBirthSchema

pytestmark = pytest.mark.django_db


if TYPE_CHECKING:
    from gouthelper_ninja.users.models import Patient


class TestDateOfBirthSchema:
    def test__dateofbirth_field(self, patient: "Patient"):
        schema = DateOfBirthSchema.from_orm(patient.dateofbirth)
        assert schema.dateofbirth == patient.dateofbirth.dateofbirth

    def test__id_field(self, patient: "Patient"):
        schema = DateOfBirthSchema.from_orm(patient.dateofbirth)
        assert schema.id == patient.dateofbirth.id

        # Test that a string UUID can be used for UUID fields
        str_uuid = str(patient.dateofbirth.id)
        assert DateOfBirthSchema(
            id=str_uuid,
            patient_id=patient.id,
            dateofbirth=patient.dateofbirth.dateofbirth,
        )
        # Test that the string UUID is converted to a UUID object
        assert isinstance(schema.id, UUID)
