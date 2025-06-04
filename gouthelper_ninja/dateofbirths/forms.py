from crispy_forms.helper import FormHelper
from django.forms import Form
from django.forms import IntegerField
from django.forms import NumberInput
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from gouthelper_ninja.utils.forms import GoutHelperForm
from gouthelper_ninja.utils.helpers import yearsago_date


class DateOfBirthForm(GoutHelperForm, Form):
    dateofbirth = IntegerField(
        label=_("Age"),
        widget=NumberInput(attrs={"min": 18, "max": 120, "step": 1}),
        min_value=18,
        max_value=120,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dateofbirth"].help_text = format_lazy(
            """How old {} {}? <a href="" target="_next">Why do we need to know?</a>""",
            self.str_attrs["tobe"],
            self.str_attrs["subject_the"],
        )
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean_dateofbirth(self):
        # Overwritten to check if there is an int age and
        # convert it to a date of birth string
        dateofbirth = self.cleaned_data["dateofbirth"]
        if dateofbirth:
            if isinstance(dateofbirth, str):
                dateofbirth = int(dateofbirth)
            dateofbirth = yearsago_date(years=dateofbirth)
        return dateofbirth


class DateOfBirthFormOptional(DateOfBirthForm):
    """Subclass of DateOfBirthForm with dateofbirth field not required."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dateofbirth"].required = False
