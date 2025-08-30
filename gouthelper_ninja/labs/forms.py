from decimal import Decimal

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset
from crispy_forms.layout import Layout
from django.core.exceptions import ValidationError
from django.forms import DecimalField
from django.forms import NumberInput
from django.utils.translation import gettext_lazy as _

from gouthelper_ninja.constants import MAX_BASELINECREATININE
from gouthelper_ninja.labs.models import BaselineCreatinine
from gouthelper_ninja.utils.forms import GoutHelperForm


def validate_baselinecreatinine_max_value(value: Decimal) -> None:
    """Method that raises a ValidationError if a baselinecreatinine value is
    greater than 5 mg/dL."""
    if value > MAX_BASELINECREATININE:
        raise ValidationError(
            _(
                "A baseline creatinine greater than 5 mg/dL isn't likely. "
                "This would typically mean the patient is on dialysis.",
            ),
        )


class BaselineCreatinineForm(GoutHelperForm):
    prefix = "baselinecreatinine"
    model: type[BaselineCreatinine] = BaselineCreatinine

    value = DecimalField(
        max_digits=4,
        decimal_places=2,
        required=False,
        widget=NumberInput(attrs={"step": 0.10}),
        label="Baseline Creatinine",
        validators=[validate_baselinecreatinine_max_value],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["value"].help_text = (
            _(
                "What is %s baseline creatinine? "
                "Creatinine is typically reported in micrograms per deciliter "
                "(mg/dL).",
            )
            % self.str_attrs["subject_the_pos"]
        )
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "",
                "value",
            ),
        )
