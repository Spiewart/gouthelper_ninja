from crispy_forms.helper import FormHelper
from django.forms import ChoiceField
from django.forms import Form
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.utils.forms import GoutHelperForm


class EthnicityForm(GoutHelperForm, Form):
    ethnicity = ChoiceField(
        label=_("Ethnicity"),
        choices=Ethnicitys.choices,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ethnicity"].help_text = format_lazy(
            # TODO: add link ethnicitys:about page
            """
            What is {} ethnicity or race?
            <a href="" target="_next">Why do we need to know?</a>
            """,
            self.str_attrs["subject_the_pos"],
        )
        self.helper = FormHelper()
        self.helper.form_tag = False


class EthnicityFormOptional(EthnicityForm):
    """Subclass of EthnicityForm with ethnicity field not required."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ethnicity"].required = False
