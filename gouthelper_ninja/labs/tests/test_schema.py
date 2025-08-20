from decimal import Decimal

import pytest
from pydantic import ValidationError

from gouthelper_ninja.labs.schema import BaselineCreatinineEditSchema
from gouthelper_ninja.labs.schema import BaselineCreatinineSchema
from gouthelper_ninja.users.tests.factories import PatientFactory


def test_edit_schema_accepts_valid_value():
    schema = BaselineCreatinineEditSchema(value=Decimal("1.20"))
    serialized = schema.serialize_baseline_creatinine()
    assert serialized == {"value": Decimal("1.20")}


def test_edit_schema_rejects_out_of_range_low():
    with pytest.raises(
        ValidationError,
        match=(r"0\.5|0\.10|ensure this value|greater than or equal to"),
    ):
        BaselineCreatinineEditSchema(value=Decimal("0.10"))


def test_edit_schema_rejects_out_of_range_high():
    with pytest.raises(
        ValidationError,
        match=(r"5\.0|10\.00|less than or equal to|ensure this value"),
    ):
        BaselineCreatinineEditSchema(value=Decimal("10.00"))


def test_defaults_present():
    schema = BaselineCreatinineEditSchema(value=Decimal("1.00"))
    assert schema.lower_limit is not None
    assert schema.upper_limit is not None
    assert schema.units is not None


@pytest.mark.django_db
def test_schema_serialization_includes_patient():
    patient = PatientFactory(baselinecreatinine=True)
    schema = BaselineCreatinineSchema(
        patient_id=patient.id,
        id=patient.baselinecreatinine.id,
        value=Decimal("1.50"),
    )
    serialized = schema.serialize_baseline_creatinine()
    assert serialized["value"] == Decimal("1.50")
    assert serialized["id"] == str(patient.baselinecreatinine.id)
    assert serialized["patient_id"] == str(patient.id)


@pytest.mark.django_db
def test_schema_roundtrip():
    patient = PatientFactory(baselinecreatinine=True)
    data = {
        "patient_id": patient.id,
        "id": patient.baselinecreatinine.id,
        "value": Decimal("1.25"),
    }
    schema = BaselineCreatinineSchema(**data)
    out = schema.serialize_baseline_creatinine()
    assert out["value"] == Decimal("1.25")
    assert out["id"] == str(patient.baselinecreatinine.id)
    assert out["patient_id"] == str(patient.id)
