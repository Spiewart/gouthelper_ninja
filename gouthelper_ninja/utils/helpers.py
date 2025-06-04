import datetime
from typing import TYPE_CHECKING
from typing import Union

from django.urls import reverse

from gouthelper_ninja.genders.choices import Genders

if TYPE_CHECKING:
    from gouthelper_ninja.users.models import Patient
    from gouthelper_ninja.users.models import User


def age_calc(date_of_birth: datetime.date) -> int:
    """Function that takes a date of birth and calculates current age

    Args:
        date_of_birth (_type_): date of birth as datetime object

    Returns:
        age or None: age integer object or None
    """
    return num_years(check_for_datetime_and_convert_to_date(date_of_birth))


def check_for_datetime_and_convert_to_date(
    date_or_datetime: datetime.date | datetime.datetime,
) -> datetime.date:
    if isinstance(date_or_datetime, datetime.datetime):
        return date_or_datetime.date()
    return date_or_datetime


def is_iterable(obj) -> bool:
    """Check if an object is iterable."""
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True


def num_years(
    begin: datetime.date,
    end: datetime.date | None = None,
    tz: datetime.timezone = datetime.UTC,
) -> int:
    # https://stackoverflow.com/questions/765797/convert-timedelta-to-years
    """Function that takes a date and returns the number of years since that date.
    If no end date is provided, the current date is used.
    Args:
        begin (date): date to calculate the number of years from
        end (date, optional): date to calculate the number of years to.
            Defaults to None, which uses the current date.
    Returns:
        int: number of years since the begin date
    """
    if end is None:
        end = datetime.datetime.now(tz=tz).date()
    number_of_years = int((end - begin).days / 365.2425)
    if begin > yearsago_datetime(number_of_years, end):
        return number_of_years - 1
    return number_of_years


def get_str_attrs_dict(
    patient: Union["Patient", None] = None,
    request_user: Union["User", None] = None,
) -> dict[str, str]:
    gender = patient.gender.gender if patient and hasattr(patient, "gender") else None

    str_attrs = {}
    if patient:
        if request_user and request_user == patient:
            str_attrs.update(
                {
                    "query": "do",
                    "tobe": "are",
                    "tobe_past": "were",
                    "tobe_neg": "aren't",
                    "pos": "have",
                    "pos_past": "had",
                    "pos_neg": "don't have",
                    "pos_neg_past": "haven't had",
                    "subject": "you",
                    "subject_the": "you",
                    "subject_pos": "your",
                    "subject_the_pos": "your",
                    "gender_pos": (
                        "hers"
                        if gender == Genders.FEMALE
                        else "his"
                        if gender == Genders.MALE
                        else "his or hers"
                    ),
                    "gender_subject": (
                        "she"
                        if gender == Genders.FEMALE
                        else "he"
                        if gender == Genders.MALE
                        else "he or she"
                    ),
                    "gender_ref": "her"
                    if gender == Genders.FEMALE
                    else "him"
                    if gender == Genders.MALE
                    else "him or her",
                },
            )
            str_attrs.update(
                {key.capitalize(): val.capitalize() for key, val in str_attrs.items()},
            )
        else:
            str_attrs.update(
                {
                    "query": "does",
                    "tobe": "is",
                    "tobe_past": "was",
                    "tobe_neg": "isn't",
                    "pos": "has",
                    "pos_past": "had",
                    "pos_neg": "doesn't have",
                    "pos_neg_past": "hasn't had",
                    "gender_pos": (
                        "her"
                        if gender == Genders.FEMALE
                        else "his"
                        if gender == Genders.MALE
                        else "his or hers"
                    ),
                    "gender_subject": (
                        "she"
                        if gender == Genders.FEMALE
                        else "he"
                        if gender == Genders.MALE
                        else "he or she"
                    ),
                    "gender_ref": (
                        "her"
                        if gender == Genders.FEMALE
                        else "him"
                        if gender == Genders.MALE
                        else "him or her"
                    ),
                },
            )
            str_attrs.update(
                {key.capitalize(): val.capitalize() for key, val in str_attrs.items()},
            )
            subject_dict = {
                "subject": str(patient),
                "subject_the": str(patient),
                "subject_pos": f"{patient!s}'s",
                "subject_the_pos": f"{patient!s}'s",
            }
            subject_dict.update(
                {key.capitalize(): val for key, val in subject_dict.items()},
            )
            str_attrs.update(subject_dict)
    else:
        str_attrs.update(
            {
                "query": "does",
                "tobe": "is",
                "tobe_past": "was",
                "tobe_neg": "isn't",
                "pos": "has",
                "pos_past": "had",
                "pos_neg": "doesn't have",
                "pos_neg_past": "hasn't had",
                "subject": "patient",
                "subject_the": "the patient",
                "subject_pos": "patient's",
                "subject_the_pos": "the patient's",
                "gender_pos": (
                    "her"
                    if gender == Genders.FEMALE
                    else "his"
                    if gender == Genders.MALE
                    else "his or her"
                ),
                "gender_subject": (
                    "she"
                    if gender == Genders.FEMALE
                    else "he"
                    if gender == Genders.MALE
                    else "he or she"
                ),
                "gender_ref": (
                    "her"
                    if gender == Genders.FEMALE
                    else "him"
                    if gender == Genders.MALE
                    else "him or her"
                ),
            },
        )
        str_attrs.update(
            {key.capitalize(): val.capitalize() for key, val in str_attrs.items()},
        )
    return str_attrs


def get_user_change(instance, request, **kwargs):  # pylint:disable=W0613
    # https://django-simple-history.readthedocs.io/en/latest/user_tracking.html
    """Method for django-simple-history to assign the user who made the change
    to the HistoricalUser history_user field. Written to deal with the case where
    the User is deleting his or her own profile and setting the history_user
    to the User's id will result in an IntegrityError."""
    # Check if the user is authenticated and the user is the User instance
    # and if the url for the request is for the User's deletion
    if request and request.user and request.user.is_authenticated:
        if request.user == instance and request.path.endswith(reverse("users:delete")):
            # Set the history_user to None
            return None
        # Otherwise, return the request.user
        return request.user
    # Otherwise, return None
    return None


def yearsago_datetime(
    years,
    from_date=None,
    tz: datetime.timezone = datetime.UTC,
):
    """Method that takes an age, or number of years, and
    returns a date of birth string. If no from_date is provided,
    the current date is used. Adjusts for leap years."""
    # https://stackoverflow.com/questions/765797/convert-timedelta-to-years
    if from_date is None:
        from_date = datetime.datetime.now(tz=tz)
    try:
        return from_date.replace(year=from_date.year - years)
    except ValueError:
        # Must be 2/29!
        return from_date.replace(month=2, day=28, year=from_date.year - years)


def yearsago_date(
    years,
    from_date=None,
    tz: datetime.timezone = datetime.UTC,
):
    """Method that takes an age, or number of years, and
    returns a date of birth string. If no from_date is provided,
    the current date is used. Adjusts for leap years."""
    from_date = (
        from_date.date() if isinstance(from_date, datetime.datetime) else from_date
    )
    return yearsago_datetime(years, from_date, tz).date()
