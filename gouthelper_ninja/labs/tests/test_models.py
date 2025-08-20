from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.db import transaction

from gouthelper_ninja.labs.choices import CreatinineLimits
from gouthelper_ninja.labs.choices import Units
from gouthelper_ninja.labs.models import BaselineCreatinine
from gouthelper_ninja.labs.tests.factories import BaselineCreatinineFactory
from gouthelper_ninja.users.tests.factories import PatientFactory

pytestmark = pytest.mark.django_db


class TestBaselineCreatinine:
    def test_constraint_units_limits_valid(self):
        patient = PatientFactory()
        # Valid: default values should work
        creatinine = BaselineCreatinine.objects.create(
            patient=patient,
            value=Decimal("1.20"),
        )
        assert creatinine.lower_limit == CreatinineLimits.LOWERMGDL
        assert creatinine.units == Units.MGDL
        assert creatinine.upper_limit == CreatinineLimits.UPPERMGDL

        # Valid: explicit valid values
        BaselineCreatinine.objects.create(
            patient=PatientFactory(),
            value=Decimal("1.50"),
            lower_limit=CreatinineLimits.LOWERMGDL,
            units=Units.MGDL,
            upper_limit=CreatinineLimits.UPPERMGDL,
        )

    def test_constraint_units_limits_invalid(self):
        patient = PatientFactory()
        # Invalid: wrong lower_limit for MGDL units
        with pytest.raises(IntegrityError), transaction.atomic():
            BaselineCreatinine.objects.create(
                patient=patient,
                value=Decimal("1.20"),
                lower_limit=Decimal("0.50"),  # Wrong limit
            )

        # Invalid: wrong upper_limit for MGDL units
        with pytest.raises(IntegrityError), transaction.atomic():
            BaselineCreatinine.objects.create(
                patient=PatientFactory(),
                value=Decimal("1.20"),
                upper_limit=Decimal("20.00"),  # Wrong limit
            )

        # Invalid: wrong units with correct limits
        with pytest.raises(IntegrityError), transaction.atomic():
            BaselineCreatinine.objects.create(
                patient=PatientFactory(),
                value=Decimal("8.0"),
                units="INVALID",  # Wrong units
            )

    def test_value_str_property(self):
        creatinine = BaselineCreatinineFactory(
            value=Decimal("1.234"),
        )
        # Should format to 2 decimal places with units
        assert creatinine.value_str == "1.23 mg/dL"

        # Test with different value
        creatinine.value = Decimal("2.567")
        creatinine.save()
        assert creatinine.value_str == "2.57 mg/dL"

    def test_str_method(self):
        creatinine = BaselineCreatinineFactory(
            value=Decimal("1.50"),
        )
        # Should include "Baseline" prefix
        assert str(creatinine) == "Baseline Creatinine: 1.50 mg/dL"

    def test_creatinine_base_str_method(self):
        creatinine = BaselineCreatinineFactory(
            value=Decimal("1.80"),
        )
        # Test the parent class __str__ method through value_str
        # The BaselineCreatinine.__str__ should call super().__str__()
        # which returns the CreatinineBase.__str__()
        assert "Creatinine: 1.80 mg/dL" in str(creatinine)

    def test_decimal_field_precision(self):
        patient = PatientFactory()
        # Test that decimal fields accept proper precision
        creatinine = BaselineCreatinine.objects.create(
            patient=patient,
            value=Decimal("12.34"),  # max_digits=4, decimal_places=2
        )
        assert creatinine.value == Decimal("12.34")

    def test_one_to_one_patient_relationship(self):
        patient = PatientFactory()
        creatinine = BaselineCreatinine.objects.create(
            patient=patient,
            value=Decimal("1.20"),
        )
        assert creatinine.patient == patient

        # Test reverse relationship
        assert hasattr(patient, "baselinecreatinine")
        assert patient.baselinecreatinine == creatinine

        # Test that creating another creatinine for same patient raises error
        with pytest.raises(IntegrityError), transaction.atomic():
            BaselineCreatinine.objects.create(
                patient=patient,
                value=Decimal("1.50"),
            )

    def test_historical_records(self):
        patient = PatientFactory()
        creatinine = BaselineCreatinine.objects.create(
            patient=patient,
            value=Decimal("1.20"),
        )
        assert creatinine.history.count() == 1
        initial_history = creatinine.history.first()
        assert initial_history.history_type == "+"
        assert initial_history.value == Decimal("1.20")

        # Update
        creatinine.value = Decimal("1.50")
        creatinine.save()
        expected_num_histories = 2
        assert creatinine.history.count() == expected_num_histories
        latest_history = creatinine.history.first()
        assert latest_history.history_type == "~"
        assert latest_history.value == Decimal("1.50")

    def test_class_attributes(self):
        # Test that class attributes from CreatinineBase are accessible
        assert BaselineCreatinine.CreatinineLimits == CreatinineLimits
        assert BaselineCreatinine.Units == Units

    def test_default_values(self):
        patient = PatientFactory()
        creatinine = BaselineCreatinine.objects.create(
            patient=patient,
            value=Decimal("1.20"),
        )
        # Check that defaults are set correctly
        assert creatinine.lower_limit == CreatinineLimits.LOWERMGDL
        assert creatinine.units == Units.MGDL
        assert creatinine.upper_limit == CreatinineLimits.UPPERMGDL
