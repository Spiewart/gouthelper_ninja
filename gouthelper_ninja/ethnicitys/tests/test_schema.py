from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from gouthelper_ninja.ethnicitys.schema import EthnicitySchema

pytestmark = pytest.mark.django_db


if TYPE_CHECKING:
    from gouthelper_ninja.users.models import Patient


class TestEthnicitySchema:
    def test__ethnicity_field(self, patient: "Patient"):
        schema = EthnicitySchema.from_orm(patient.ethnicity)
        assert schema.ethnicity == patient.ethnicity.ethnicity

    def test__id_field(self, patient: "Patient"):
        schema = EthnicitySchema.from_orm(patient.ethnicity)
        assert schema.id == patient.ethnicity.id

        # Test that a string UUID can be used for UUID fields
        str_uuid = str(patient.ethnicity.id)
        assert EthnicitySchema(
            id=str_uuid,
            patient_id=patient.id,
            ethnicity=patient.ethnicity.ethnicity,
        )
        # Test that the string UUID is converted to a UUID object
        assert isinstance(schema.id, UUID)
