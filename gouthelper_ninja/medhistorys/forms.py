from crispy_forms.helper import FormHelper
from django.core.exceptions import ValidationError
from django.forms import NullBooleanField
from django.utils.translation import gettext_lazy as _

from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.utils.forms import GoutHelperForm


class MedHistoryForm(GoutHelperForm):
    class Meta:
        fields = ("history_of",)

    history_of = NullBooleanField(
        # Set the label to a placeholder
        label=_("MedHistory"),
        initial=None,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop("model")
        optional = kwargs.pop("optional", False)
        super().__init__(*args, **kwargs)
        self.mhtype = MHTypes(self.model.__name__.upper())
        if optional:
            self.fields["history_of"].required = False
        self.fields["history_of"].label = self.mhtype.label
        self.fields["history_of"].help_text = (
            f"Does {self.str_attrs.get('subject')} "
            f"{self.str_attrs.get('subject_pos')} "
            f"a history of {self.mhtype.label}?"
        )
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean_history_of(self):
        data = self.cleaned_data["history_of"]
        if data is None:
            raise ValidationError(_("This field is required."))
        return data
