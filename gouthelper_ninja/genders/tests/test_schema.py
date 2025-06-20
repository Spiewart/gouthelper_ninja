from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from gouthelper_ninja.genders.schema import GenderSchema

pytestmark = pytest.mark.django_db


if TYPE_CHECKING:
    from gouthelper_ninja.users.models import Patient


class TestGenderSchema:
    def test__gender_field(self, patient: "Patient"):
        schema = GenderSchema.from_orm(patient.gender)
        assert schema.gender == patient.gender.gender

    def test__id_field(self, patient: "Patient"):
        schema = GenderSchema.from_orm(patient.gender)
        assert schema.id == patient.gender.id

        # Test that a string UUID can be used for UUID fields
        str_uuid = str(patient.gender.id)
        assert GenderSchema(
            id=str_uuid,
            patient_id=patient.id,
            gender=patient.gender.gender,
        )
        # Test that the string UUID is converted to a UUID object
        assert isinstance(schema.id, UUID)
