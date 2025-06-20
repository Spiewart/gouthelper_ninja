from crispy_forms.helper import FormHelper
from django.forms import ChoiceField
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.models import Gender
from gouthelper_ninja.utils.forms import GoutHelperForm


class GenderForm(GoutHelperForm):
    model = Gender

    gender = ChoiceField(
        label=_("Gender"),
        choices=Genders.choices,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["gender"].help_text = format_lazy(
            # TODO: add link genders:about page
            """
            What is {} biological sex? <a href="" target="_next">
            Why do we need to know?</a>
            """,
            self.str_attrs["subject_the_pos"],
        )
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean_gender(self):
        """Converts string representations of the Genders enum
        to the enum itself."""
        gender = self.cleaned_data.get("gender")
        if gender is not None and gender != "":
            self.cleaned_data["gender"] = Genders(int(gender))
        else:
            self.cleaned_data["gender"] = None
        return self.cleaned_data["gender"]


class GenderFormOptional(GenderForm):
    """Subclass of GenderForm with gender field not required."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["gender"].required = False
