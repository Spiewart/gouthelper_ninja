from datetime import date
from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone

from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.dateofbirths.tests.factories import DateOfBirthFactory
from gouthelper_ninja.users.tests.factories import PatientFactory

pytestmark = pytest.mark.django_db


class TestDateOfBirthModel:
    def test_str_representation(self):
        dob_date = date(2000, 1, 1)
        dob = DateOfBirthFactory(dateofbirth=dob_date)
        assert str(dob) == "2000-01-01"

    def test_get_absolute_url(self):
        patient = PatientFactory()
        assert patient.dateofbirth.get_absolute_url() == patient.get_absolute_url()

    def test_update_method_changes_date(self):
        dob = DateOfBirthFactory(dateofbirth=date(1990, 5, 15))
        new_date = date(1992, 8, 20)
        data = DateOfBirthEditSchema(dateofbirth=new_date)
        updated_dob = dob.update(data)

        assert updated_dob.dateofbirth == new_date
        # Verify it's saved in the database
        dob.refresh_from_db()
        assert dob.dateofbirth == new_date

    def test_update_method_no_change(self):
        original_date = date(1985, 3, 10)
        dob = DateOfBirthFactory(dateofbirth=original_date)
        # Mock save to ensure it's not called if date doesn't change
        original_save = dob.save
        save_called = False

        def mock_save(*args, **kwargs):
            nonlocal save_called
            save_called = True
            original_save(*args, **kwargs)

        dob.save = mock_save

        data = DateOfBirthEditSchema(dateofbirth=original_date)
        updated_dob = dob.update(data)

        assert updated_dob.dateofbirth == original_date
        assert not save_called
        dob.save = original_save  # Restore original save method

    def test_dateofbirth_valid_constraint_pass(self):
        # Date of birth 18 years ago or more
        valid_dob = timezone.now().date() - timedelta(days=365 * 18)
        try:
            DateOfBirthFactory(dateofbirth=valid_dob)
        except IntegrityError:  # pragma: no cover
            pytest.fail("IntegrityError raised for valid date of birth")

    def test_dateofbirth_valid_constraint_fail(self):
        # Date of birth less than 18 years ago
        invalid_dob = timezone.now().date() - timedelta(days=365 * 17)
        with pytest.raises(IntegrityError):
            DateOfBirthFactory(dateofbirth=invalid_dob)

    def test_historical_records(self):
        dob = DateOfBirthFactory()
        old_date = dob.dateofbirth
        new_date = old_date - timedelta(days=365)  # Change by one year
        dob.dateofbirth = new_date
        dob.save()

        expected_history_count = 2
        assert dob.history.count() == expected_history_count

        first_history = dob.history.last()  # first is the creation
        assert first_history.history_type == "+"
        assert first_history.dateofbirth == old_date
        second_history = dob.history.first()  # last is the update
        assert second_history.history_type == "~"
        assert second_history.dateofbirth == new_date
