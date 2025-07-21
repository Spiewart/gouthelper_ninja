import datetime
from uuid import UUID

import pytest

from gouthelper_ninja.constants import MAX_MENOPAUSE_AGE
from gouthelper_ninja.constants import MIN_MENOPAUSE_AGE
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.utils import helpers
from gouthelper_ninja.utils.helpers import menopause_required


class DummyPatient:
    def __init__(self, gender=None):
        # Always set .gender to an object with a .gender attribute
        self.gender = type("Gender", (), {"gender": gender})()

    def __str__(self):
        return "John Doe"


class DummyUser:
    def __init__(self, id=1, gender=None):  # noqa: A002
        self.id = id
        self.gender = type("Gender", (), {"gender": gender})()
        self.is_authenticated = True

    def __str__(self):
        return "John Doe"


# age_calc
def test_age_calc():
    today = datetime.datetime.now(tz=datetime.UTC).date()
    years_ago = 30
    dob = today.replace(year=today.year - years_ago)
    assert helpers.age_calc(dob) == years_ago


# check_for_datetime_and_convert_to_date
def test_check_for_datetime_and_convert_to_date():
    d = datetime.date(2020, 1, 1)
    dt = datetime.datetime(2020, 1, 1, tzinfo=datetime.UTC)
    assert helpers.check_for_datetime_and_convert_to_date(d) == d
    assert helpers.check_for_datetime_and_convert_to_date(dt) == d


# is_iterable
def test_is_iterable():
    assert helpers.is_iterable([1, 2, 3])
    assert not helpers.is_iterable(123)


# is_valid_uuid
def test_is_valid_uuid():
    u = UUID("12345678-1234-5678-1234-567812345678")
    assert helpers.is_valid_uuid(str(u)) == u
    assert helpers.is_valid_uuid(u) == u
    assert helpers.is_valid_uuid("not-a-uuid") is False


# num_years
def test_num_years():
    expected_years = 10
    expected_leap_years = 9
    today = datetime.datetime.now(tz=datetime.UTC).date()
    d = today.replace(year=today.year - 10)
    assert (
        helpers.num_years(d) == expected_years
        or helpers.num_years(d) == expected_leap_years
    )  # leap years


# get_str_attrs_dict
@pytest.mark.parametrize(
    ("patient", "request_user", "gender", "expected_subject"),
    [
        # For 'you', patient and request_user must be the same object
        (DummyPatient(Genders.FEMALE), None, Genders.FEMALE, "you"),
        (DummyPatient(Genders.MALE), None, Genders.MALE, "you"),
        (
            DummyPatient(Genders.FEMALE),
            DummyUser(gender=Genders.MALE),
            Genders.FEMALE,
            "John Doe",
        ),
        (None, None, None, "patient"),
    ],
)
def test_get_str_attrs_dict(patient, request_user, gender, expected_subject):
    if expected_subject == "you":
        # Use the same object for both patient and request_user
        request_user = patient
    d = helpers.get_str_attrs_dict(patient, request_user)
    assert "subject" in d
    assert d["subject"].lower().startswith(expected_subject.lower())


# yearsago_datetime and yearsago_date
def test_yearsago_datetime_and_date():
    expected_year = 2010
    now = datetime.datetime(2020, 6, 27, tzinfo=datetime.UTC)
    dt = helpers.yearsago_datetime(10, now)
    assert dt.year == expected_year
    d = helpers.yearsago_date(10, now)
    assert d.year == expected_year


# get_user_change
def test_get_user_change_authenticated():
    class DummyRequest:
        def __init__(self, user, path):
            self.user = user
            self.path = path

    user = DummyUser(id=1)
    patient = DummyUser(id=1)
    instance = type("Instance", (), {"patient": patient})()
    request = DummyRequest(user, "/users/~delete/")
    # Should return None if deleting self
    assert helpers.get_user_change(instance, request) is None
    # Should return user if not deleting self
    request2 = DummyRequest(user, "/users/other/")
    assert helpers.get_user_change(instance, request2) == user
    # Should return None if not authenticated
    user2 = DummyUser(id=2)
    user2.is_authenticated = False
    request3 = DummyRequest(user2, "/users/~delete/")
    assert helpers.get_user_change(instance, request3) is None


def make_birthdate(years_ago):
    today = datetime.datetime.now(tz=datetime.UTC).date()
    return today.replace(year=today.year - years_ago)


def test_menopause_required_true():
    # Female, age in range
    age = (MIN_MENOPAUSE_AGE + MAX_MENOPAUSE_AGE) // 2
    dob = make_birthdate(age)
    assert menopause_required(dob, Genders.FEMALE) is True


def test_menopause_required_false_wrong_gender():
    # Male, age in range
    age = (MIN_MENOPAUSE_AGE + MAX_MENOPAUSE_AGE) // 2
    dob = make_birthdate(age)
    assert menopause_required(dob, Genders.MALE) is False


def test_menopause_required_false_too_young():
    # Female, too young
    dob = make_birthdate(MIN_MENOPAUSE_AGE - 1)
    assert menopause_required(dob, Genders.FEMALE) is False


def test_menopause_required_false_too_old():
    # Female, too old
    dob = make_birthdate(MAX_MENOPAUSE_AGE)
    assert menopause_required(dob, Genders.FEMALE) is False


def test_menopause_required_edge_cases():
    # Female, exactly at min age
    dob = make_birthdate(MIN_MENOPAUSE_AGE)
    assert menopause_required(dob, Genders.FEMALE) is True
    # Female, just below max age
    dob = make_birthdate(MAX_MENOPAUSE_AGE - 1)
    assert menopause_required(dob, Genders.FEMALE) is True
    assert menopause_required(dob, Genders.FEMALE) is True
