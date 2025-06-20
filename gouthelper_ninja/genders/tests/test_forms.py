import pytest
from django.utils.text import format_lazy

from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.forms import GenderForm
from gouthelper_ninja.genders.forms import GenderFormOptional


@pytest.fixture
def data():
    """Fixture to provide mock data for testing."""
    return {"gender": Genders.MALE.value}


@pytest.fixture
def form_kwargs():
    """Fixture to provide mock form kwargs."""
    return {
        "request_user": None,
        "str_attrs": {"subject_the_pos": "the patient's"},
        "patient": None,  # Assuming patient is not needed for this test
    }


class TestGenderForm:
    def test_valid_data(self, data, form_kwargs):
        form = GenderForm(data=data, **form_kwargs)
        assert form.is_valid()
        assert form.cleaned_data["gender"] == Genders.MALE.value

    def test_help_text_format(self, form_kwargs):
        form = GenderForm(**form_kwargs)
        # Access str_attrs from the form instance as it's set in __init__
        expected_help_text = format_lazy(
            """
            What is {} biological sex? <a href="" target="_next">
            Why do we need to know?</a>
            """,
            form.str_attrs["subject_the_pos"],
        )
        assert form.fields["gender"].help_text == expected_help_text

    def test_form_tag_false(self, form_kwargs):
        form = GenderForm(data={}, **form_kwargs)
        form.is_valid()  # Trigger form initialization
        assert form.helper.form_tag is False

    def test_field_required(self, form_kwargs):
        form = GenderForm(data={}, **form_kwargs)
        assert not form.is_valid()
        assert "gender" in form.errors
        assert form.fields["gender"].required is True

    @pytest.mark.parametrize(
        "invalid_gender_data",
        [
            {"gender": "INVALID_CHOICE"},
            {"gender": 99},  # Invalid integer choice
            {"gender": None},  # Explicitly None when required
        ],
    )
    def test_invalid_gender(self, invalid_gender_data, form_kwargs):
        form = GenderForm(data=invalid_gender_data, **form_kwargs)
        assert not form.is_valid()
        assert "gender" in form.errors

    @pytest.mark.parametrize(
        ("input_value", "expected_enum"),
        [
            (str(Genders.MALE.value), Genders.MALE),
            (str(Genders.FEMALE.value), Genders.FEMALE),
            (Genders.MALE.value, Genders.MALE),  # Test integer input too
            (Genders.FEMALE.value, Genders.FEMALE),  # Test integer input too
        ],
    )
    def test_clean_gender(self, input_value, expected_enum, form_kwargs):
        """Tests the clean_gender method correctly converts input to enum."""
        form = GenderForm(data={"gender": input_value}, **form_kwargs)
        # Call is_valid() to populate cleaned_data before calling clean_gender
        assert form.is_valid()

        cleaned_value = form.clean_gender()
        assert isinstance(cleaned_value, Genders)
        assert cleaned_value == expected_enum


class TestGenderFormOptional:
    def test_field_not_required(self, form_kwargs):
        # Test with empty data, field should not be required
        form = GenderFormOptional(data={}, **form_kwargs)
        assert form.is_valid()
        assert "gender" not in form.errors
        assert form.fields["gender"].required is False

    def test_valid_data_optional(self, data, form_kwargs):
        # Test with valid data provided
        form = GenderFormOptional(data=data, **form_kwargs)
        assert form.is_valid()
        assert form.cleaned_data["gender"] == Genders.MALE.value

    def test_empty_data_optional(self, form_kwargs):
        # Test with gender explicitly set to empty string
        form = GenderFormOptional(data={"gender": ""}, **form_kwargs)
        assert form.is_valid()
        # For a ChoiceField, an empty value when not required results in None or empty
        # string depending on `empty_value` which defaults to "" for ChoiceField.
        # If you expect None, you might need to adjust the field or clean method.
        assert form.cleaned_data.get("gender") in [None, ""]

        # Test with no gender key in data
        form = GenderFormOptional(data={}, **form_kwargs)
        assert form.is_valid()
        assert form.cleaned_data.get("gender") in [None, ""]

    def test_form_tag_false_optional(self, form_kwargs):
        form = GenderFormOptional(data={}, **form_kwargs)
        form.is_valid()  # Trigger form initialization
        assert form.helper.form_tag is False

    def test_invalid_data_optional(self, form_kwargs):
        # Even if optional, if data is provided, it should be valid
        form = GenderFormOptional(data={"gender": "INVALID_CHOICE"}, **form_kwargs)
        assert not form.is_valid()
        assert "gender" in form.errors

    @pytest.mark.parametrize(
        ("input_value", "expected_cleaned_value"),
        [
            (str(Genders.MALE.value), Genders.MALE),
            (str(Genders.FEMALE.value), Genders.FEMALE),
            (Genders.MALE.value, Genders.MALE),
            (Genders.FEMALE.value, Genders.FEMALE),
            (None, None),  # Test None input
            ("", None),  # Test empty string input
        ],
    )
    def test_clean_gender_optional(
        self,
        input_value,
        expected_cleaned_value,
        form_kwargs,
    ):
        """Tests the clean_gender method for the optional form."""
        form = GenderFormOptional(
            data={"gender": input_value} if input_value is not None else {},
            **form_kwargs,
        )
        assert form.is_valid()  # Should be valid for None or empty string

        assert form.cleaned_data.get("gender") == expected_cleaned_value
