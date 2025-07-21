import datetime

import pytest
from pydantic import ValidationError

from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.ethnicitys.schema import EthnicityEditSchema
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.schema import GenderEditSchema
from gouthelper_ninja.goutdetails.schema import GoutDetailEditSchema
from gouthelper_ninja.medhistorys.schema import MedHistoryEditSchema
from gouthelper_ninja.users.schema import PatientEditSchema


def make_patient_data(
    dateofbirth_years_ago=50,
    gender=Genders.FEMALE,
    menopause=None,
):
    today = datetime.datetime.now(tz=datetime.UTC).date()
    dob = today.replace(year=today.year - dateofbirth_years_ago)
    return {
        "dateofbirth": DateOfBirthEditSchema(dateofbirth=dob),
        "ethnicity": EthnicityEditSchema(ethnicity=Ethnicitys.CAUCASIAN),
        "gender": GenderEditSchema(gender=gender),
        "gout": MedHistoryEditSchema(history_of=True),
        "goutdetail": GoutDetailEditSchema(at_goal=True),
        "menopause": menopause,
    }


def test_patient_edit_schema_valid_with_menopause():
    data = make_patient_data(menopause=MedHistoryEditSchema(history_of=True))
    schema = PatientEditSchema(**data)
    assert schema.menopause is not None


def test_patient_edit_schema_valid_not_required():
    # Male, menopause not required
    data = make_patient_data(gender=Genders.MALE)
    schema = PatientEditSchema(**data)
    assert schema.menopause is None
    # Female, too young
    data = make_patient_data(dateofbirth_years_ago=20)
    schema = PatientEditSchema(**data)
    assert schema.menopause is None
    # Female, too old
    data = make_patient_data(dateofbirth_years_ago=80)
    schema = PatientEditSchema(**data)
    assert schema.menopause is None


def test_patient_edit_schema_invalid_missing_menopause():
    # Female, age in menopause-required range, menopause missing
    data = make_patient_data()
    with pytest.raises(ValidationError) as exc:
        PatientEditSchema(**data)
    assert "menopause status" in str(exc.value)
    with pytest.raises(ValidationError) as exc:
        PatientEditSchema(**data)
    assert "menopause status" in str(exc.value)
