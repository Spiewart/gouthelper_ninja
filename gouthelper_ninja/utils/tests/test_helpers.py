import datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from freezegun import freeze_time

from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory
from gouthelper_ninja.utils.helpers import age_calc
from gouthelper_ninja.utils.helpers import check_for_datetime_and_convert_to_date
from gouthelper_ninja.utils.helpers import get_str_attrs_dict
from gouthelper_ninja.utils.helpers import get_user_change
from gouthelper_ninja.utils.helpers import is_iterable
from gouthelper_ninja.utils.helpers import is_valid_uuid
from gouthelper_ninja.utils.helpers import num_years
from gouthelper_ninja.utils.helpers import yearsago_date
from gouthelper_ninja.utils.helpers import yearsago_datetime

pytestmark = pytest.mark.django_db


class TestHelperFunctions(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @freeze_time("2023-10-27")
    def test_age_calc(self):
        dob_date = datetime.date(1990, 10, 27)
        expected_age = 33
        assert age_calc(dob_date) == expected_age
        dob_datetime = datetime.datetime(
            1990,
            10,
            27,
            10,
            0,
            0,
            tzinfo=datetime.UTC,
        )
        assert age_calc(dob_datetime) == expected_age
        # Test birthday not yet passed this year
        dob_not_yet = datetime.date(1990, 10, 28)
        expected_age_not_yet = 32
        assert age_calc(dob_not_yet) == expected_age_not_yet

    def test_check_for_datetime_and_convert_to_date(self):
        dt = datetime.datetime(
            2023,
            1,
            1,
            12,
            0,
            0,
            tzinfo=datetime.UTC,
        )
        d = datetime.date(2023, 1, 1)
        assert check_for_datetime_and_convert_to_date(dt) == d
        assert check_for_datetime_and_convert_to_date(d) == d

    def test_is_iterable(self):
        assert is_iterable([])
        assert is_iterable(())
        assert is_iterable("string")
        assert is_iterable({})
        assert not is_iterable(123)
        assert not is_iterable(True)  # noqa: FBT003
        assert not is_iterable(None)

    def test_is_valid_uuid(self):
        valid_uuid = uuid4()
        assert is_valid_uuid(str(valid_uuid)) == valid_uuid
        assert is_valid_uuid(valid_uuid) == valid_uuid
        assert not is_valid_uuid("not-a-uuid")
        assert not is_valid_uuid(123)
        assert not is_valid_uuid(None)

    @freeze_time("2023-10-27")
    def test_num_years(self):
        begin_date = datetime.date(2020, 1, 1)
        end_date = datetime.date(2023, 1, 1)
        expected_years = 3
        assert num_years(begin_date, end_date) == expected_years
        # Test with no end date
        assert num_years(begin_date) == expected_years
        # Test edge case where birthday hasn't passed
        begin_date_edge = datetime.date(2020, 10, 28)
        expected_years = 2
        assert num_years(begin_date_edge) == expected_years
        # Test leap year
        begin_leap = datetime.date(2020, 2, 29)
        end_leap = datetime.date(2024, 2, 28)
        expected_years = 3
        assert num_years(begin_leap, end_leap) == expected_years
        end_leap_after = datetime.date(2024, 3, 1)
        expected_years = 4
        assert num_years(begin_leap, end_leap_after) == expected_years

    def test_get_str_attrs_dict(self):
        # Scenario 1: No patient
        attrs = get_str_attrs_dict()
        assert attrs["subject"] == "patient"
        assert attrs["subject_the"] == "the patient"
        assert attrs["gender_pos"] == "his or her"

        # Scenario 2: Patient exists, request_user is None
        patient = PatientFactory(gender__gender=Genders.MALE)
        attrs = get_str_attrs_dict(patient=patient)
        assert attrs["subject"] == str(patient)
        assert attrs["gender_pos"] == "his"
        assert attrs["pos"] == "has"

        # Scenario 3: request_user is the patient
        attrs = get_str_attrs_dict(patient=patient, request_user=patient)
        assert attrs["subject"] == "you"
        assert attrs["gender_pos"] == "his"
        assert attrs["pos"] == "have"

        # Scenario 4: request_user is different from patient
        provider = UserFactory()
        attrs = get_str_attrs_dict(patient=patient, request_user=provider)
        assert attrs["subject"] == str(patient)
        assert attrs["gender_pos"] == "his"
        assert attrs["pos"] == "has"

        # Scenario 5: Patient is female
        patient_female = PatientFactory(gender__gender=Genders.FEMALE)
        attrs = get_str_attrs_dict(patient=patient_female)
        assert attrs["gender_pos"] == "her"
        attrs_self = get_str_attrs_dict(
            patient=patient_female,
            request_user=patient_female,
        )
        assert attrs_self["gender_pos"] == "hers"

    def test_get_user_change(self):
        user = UserFactory()
        # Create a mock instance with a 'patient' attribute
        mock_instance_with_patient = Mock()
        mock_instance_with_patient.patient = user

        # Scenario 1: request.user is authenticated and not the instance
        other_user = UserFactory()
        request = self.factory.get("/fake-url/")
        request.user = other_user
        assert get_user_change(mock_instance_with_patient, request) == other_user

        # Scenario 2: request.user is the instance, but not delete path
        request.user = user
        assert get_user_change(mock_instance_with_patient, request) == user

        # Scenario 3: request.user is instance, and it is delete path
        delete_url = reverse("users:delete")
        request = self.factory.get(delete_url)
        request.user = user
        assert get_user_change(mock_instance_with_patient, request) is None

        # Scenario 4: user is not authenticated
        request.user = AnonymousUser()
        assert get_user_change(mock_instance_with_patient, request) is None

        # Scenario 5: no request
        assert get_user_change(mock_instance_with_patient, None) is None

    def test_yearsago_datetime(self):
        from_date = datetime.datetime(2023, 10, 27, 12, 0, 0, tzinfo=datetime.UTC)
        result = yearsago_datetime(10, from_date)
        e_year, e_month, e_day = 2013, 10, 27
        assert result.year == e_year
        assert result.month == e_month
        assert result.day == e_day

        # Test leap year from Feb 29
        from_leap = datetime.datetime(2024, 2, 29, 12, 0, 0, tzinfo=datetime.UTC)
        result_leap = yearsago_datetime(4, from_leap)
        e_year, e_month, e_day = 2020, 2, 29
        assert result_leap.year == e_year
        assert result_leap.month == e_month
        assert result_leap.day == e_day

        # Test leap year to non-leap year (Feb 29 -> Feb 28)
        from_leap_to_non = datetime.datetime(2020, 2, 29, 12, 0, 0, tzinfo=datetime.UTC)
        result_leap_to_non = yearsago_datetime(1, from_leap_to_non)
        e_year, e_month, e_day = 2019, 2, 28
        assert result_leap_to_non.year == e_year
        assert result_leap_to_non.month == e_month
        assert result_leap_to_non.day == e_day

    @freeze_time("2023-10-27")
    def test_yearsago_date(self):
        result = yearsago_date(10)
        assert result == datetime.date(2013, 10, 27)

        from_date = datetime.date(2023, 10, 27)
        result_from = yearsago_date(10, from_date)
        assert result_from == datetime.date(2013, 10, 27)

        # Test leap year
        from_leap = datetime.date(2024, 2, 29)
        result_leap = yearsago_date(4, from_leap)
        assert result_leap == datetime.date(2020, 2, 29)
