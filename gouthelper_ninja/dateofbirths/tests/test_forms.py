from datetime import date

import pytest
from django.utils.text import format_lazy

from gouthelper_ninja.dateofbirths.forms import DateOfBirthForm
from gouthelper_ninja.dateofbirths.forms import DateOfBirthFormOptional
from gouthelper_ninja.utils.helpers import yearsago_date


@pytest.fixture
def data():
    """Fixture to provide mock data for testing."""
    return {"dateofbirth": 30}  # Example age


@pytest.fixture
def form_kwargs(data):
    """Fixture to provide mock form kwargs."""
    return {
        "request_user": None,
        "str_attrs": {"tobe": "is", "subject_the": "the patient"},
        "patient": None,  # Assuming patient is not needed for this test
    }


class TestDateOfBirthForm:
    def test_valid_data_int_age(self, data, form_kwargs):
        form = DateOfBirthForm(data=data, **form_kwargs)
        assert form.is_valid()
        assert form.cleaned_data["dateofbirth"] == yearsago_date(30)

    def test_valid_data_str_age(self, data, form_kwargs):
        data.update({"dateofbirth": "30"})
        form = DateOfBirthForm(data=data, **form_kwargs)
        assert form.is_valid()
        assert form.cleaned_data["dateofbirth"] == yearsago_date(30)

    def test_clean_dateofbirth(self, data, form_kwargs):
        form = DateOfBirthForm(data=data, **form_kwargs)
        # Mock the cleaned_data, which would be present
        # when the field clean method is called
        form.cleaned_data = {"dateofbirth": 25}

        cleaned_date = form.clean_dateofbirth()
        assert isinstance(cleaned_date, date)
        assert cleaned_date == yearsago_date(25)

        form.cleaned_data = {"dateofbirth": "40"}
        cleaned_date = form.clean_dateofbirth()
        assert isinstance(cleaned_date, date)
        assert cleaned_date == yearsago_date(40)

    def test_help_text_format(self, form_kwargs):
        form = DateOfBirthForm(**form_kwargs)
        form.str_attrs = {"tobe": "is", "subject_the": "the patient"}
        expected_help_text = format_lazy(
            """How old {} {}? <a href="" target="_next">Why do we need to know?</a>""",
            "is",
            "the patient",
        )
        assert form.fields["dateofbirth"].help_text == expected_help_text

    def test_form_tag_false(self, form_kwargs):
        form = DateOfBirthForm(data={}, **form_kwargs)
        form.is_valid()  # Trigger form initialization
        assert form.helper.form_tag is False

    def test_field_required(self, form_kwargs):
        form = DateOfBirthForm(data={}, **form_kwargs)
        form.is_valid()
        assert "dateofbirth" in form.errors
        assert form.fields["dateofbirth"].required is True

    @pytest.mark.parametrize(
        "invalid_age",
        [
            17,  # Below min
            121,  # Above max
            "abc",  # Not an int
            None,
        ],
    )
    def test_invalid_age(self, invalid_age, form_kwargs):
        data = {"dateofbirth": invalid_age}
        form = DateOfBirthForm(data=data, **form_kwargs)
        form.is_valid()
        assert "dateofbirth" in form.errors


class TestDateOfBirthFormOptional:
    def test_field_not_required(self, form_kwargs):
        data = {}
        form = DateOfBirthFormOptional(data=data, **form_kwargs)
        form.is_valid()
        assert "dateofbirth" not in form.errors
        assert form.fields["dateofbirth"].required is False

    def test_valid_data_optional(self, form_kwargs):
        data = {"dateofbirth": 45}
        form = DateOfBirthFormOptional(data=data, **form_kwargs)
        assert form.is_valid()
        assert form.cleaned_data["dateofbirth"] == yearsago_date(45)

    def test_empty_data_optional(self, form_kwargs):
        data = {"dateofbirth": ""}
        form = DateOfBirthFormOptional(data=data, **form_kwargs)
        form.is_valid()
        assert form.cleaned_data.get("dateofbirth") is None

        form = DateOfBirthFormOptional(data={}, **form_kwargs)
        assert form.is_valid()
        assert form.cleaned_data.get("dateofbirth") is None

    def test_form_tag_false_optional(self, form_kwargs):
        form = DateOfBirthFormOptional(data={}, **form_kwargs)
        form.is_valid()  # Trigger form initialization
        assert form.helper.form_tag is False
