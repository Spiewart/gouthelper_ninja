from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from gouthelper_ninja.labs.forms import BaselineCreatinineForm
from gouthelper_ninja.labs.forms import validate_baselinecreatinine_max_value


def _make_form(data: dict | None = None):
    kwargs = {
        "patient": None,
        "request_user": None,
        "str_attrs": {"subject_the_pos": "the patient"},
    }
    if data is not None:
        return BaselineCreatinineForm(data=data, **kwargs)
    return BaselineCreatinineForm(**kwargs)


def test_validator_raises_on_too_high_value():
    """Validator raises for implausible creatinine values."""
    with pytest.raises(ValidationError):
        validate_baselinecreatinine_max_value(Decimal("6.0"))


def test_form_rejects_value_above_max():
    """Binding the form with a value above the max should make it invalid."""
    form = _make_form({"baselinecreatinine-value": "6.0"})
    assert not form.is_valid()
    # error should be attached to the 'value' field
    assert "value" in form.errors


def test_form_accepts_valid_value_and_cleans_to_decimal():
    form = _make_form({"baselinecreatinine-value": "4.50"})
    assert form.is_valid()
    assert form.cleaned_data["value"] == Decimal("4.50")


def test_help_text_includes_subject():
    """Help text should include the provided str_attrs subject_the_pos."""
    form = _make_form()
    help_text = str(form.fields["value"].help_text)
    assert "the patient" in help_text
