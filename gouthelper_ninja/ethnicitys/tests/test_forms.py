import pytest
from django.utils.text import format_lazy

from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.ethnicitys.forms import EthnicityForm
from gouthelper_ninja.ethnicitys.forms import EthnicityFormOptional


@pytest.fixture
def data():
    """Fixture to provide mock data for testing."""
    return {"ethnicity": Ethnicitys.CAUCASIAN.value}


@pytest.fixture
def form_kwargs():
    """Fixture to provide mock form kwargs."""
    return {
        "request_user": None,
        "str_attrs": {"subject_the_pos": "the patient's"},
        "patient": None,  # Assuming patient is not needed for this test
    }


class TestEthnicityForm:
    def test_valid_data(self, data, form_kwargs):
        form = EthnicityForm(data=data, **form_kwargs)
        assert form.is_valid()
        assert form.cleaned_data["ethnicity"] == Ethnicitys.CAUCASIAN.value

    def test_help_text_format(self, form_kwargs):
        form = EthnicityForm(**form_kwargs)
        # Access str_attrs from the form instance as it's set in __init__
        expected_help_text = format_lazy(
            """
            What is {} ethnicity or race?
            <a href="" target="_next">Why do we need to know?</a>
            """,
            form.str_attrs["subject_the_pos"],
        )
        assert form.fields["ethnicity"].help_text == expected_help_text

    def test_form_tag_false(self, form_kwargs):
        form = EthnicityForm(data={}, **form_kwargs)
        form.is_valid()  # Trigger form initialization
        assert form.helper.form_tag is False

    def test_field_required(self, form_kwargs):
        form = EthnicityForm(data={}, **form_kwargs)
        assert not form.is_valid()
        assert "ethnicity" in form.errors
        assert form.fields["ethnicity"].required is True

    @pytest.mark.parametrize(
        "invalid_ethnicity_data",
        [
            {"ethnicity": "INVALID_CHOICE"},
            {"ethnicity": None},  # Explicitly None when required
        ],
    )
    def test_invalid_ethnicity(self, invalid_ethnicity_data, form_kwargs):
        form = EthnicityForm(data=invalid_ethnicity_data, **form_kwargs)
        assert not form.is_valid()
        assert "ethnicity" in form.errors


class TestEthnicityFormOptional:
    def test_field_not_required(self, form_kwargs):
        # Test with empty data, field should not be required
        form = EthnicityFormOptional(data={}, **form_kwargs)
        assert form.is_valid()
        assert "ethnicity" not in form.errors
        assert form.fields["ethnicity"].required is False

    def test_valid_data_optional(self, data, form_kwargs):
        # Test with valid data provided
        form = EthnicityFormOptional(data=data, **form_kwargs)
        assert form.is_valid()
        assert form.cleaned_data["ethnicity"] == Ethnicitys.CAUCASIAN.value

    def test_empty_data_optional(self, form_kwargs):
        # Test with ethnicity explicitly set to empty string
        form = EthnicityFormOptional(data={"ethnicity": ""}, **form_kwargs)
        assert form.is_valid()
        # For a ChoiceField, an empty value when not required results
        # in None or empty string
        # depending on `empty_value` which defaults to "" for ChoiceField.
        # If you expect None, you might need to adjust the field or clean method.
        # For now, we'll assert it's one of the "empty" values.
        assert form.cleaned_data.get("ethnicity") in [None, ""]

        # Test with no ethnicity key in data
        form = EthnicityFormOptional(data={}, **form_kwargs)
        assert form.is_valid()
        assert form.cleaned_data.get("ethnicity") in [None, ""]

    def test_form_tag_false_optional(self, form_kwargs):
        form = EthnicityFormOptional(data={}, **form_kwargs)
        form.is_valid()  # Trigger form initialization
        assert form.helper.form_tag is False

    def test_invalid_data_optional(self, form_kwargs):
        # Even if optional, if data is provided, it should be valid
        form = EthnicityFormOptional(
            data={"ethnicity": "INVALID_CHOICE"},
            **form_kwargs,
        )
        assert not form.is_valid()
        assert "ethnicity" in form.errors
