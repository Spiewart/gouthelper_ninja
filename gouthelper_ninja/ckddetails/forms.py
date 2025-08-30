from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import Fieldset
from crispy_forms.layout import Layout
from django.forms import BooleanField
from django.forms import ChoiceField
from django.forms import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from gouthelper_ninja.ckddetails.choices import DialysisChoices
from gouthelper_ninja.ckddetails.choices import DialysisDurations
from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.ckddetails.models import CkdDetail
from gouthelper_ninja.utils.forms import GoutHelperForm


class CkdDetailForm(GoutHelperForm):
    model = CkdDetail

    dialysis = BooleanField(
        required=False,
        initial=None,
    )
    dialysis_type = ChoiceField(
        choices=DialysisChoices.choices,
        required=False,
        initial=None,
    )
    dialysis_duration = ChoiceField(
        choices=DialysisDurations.choices,
        required=False,
        initial=None,
    )
    stage = ChoiceField(
        choices=Stages.choices,
        required=False,
        initial=None,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dialysis"].help_text = mark_safe(  # noqa: S308
            f"{self.str_attrs['Tobe']} {self.str_attrs['subject_the']} on "
            "<a href='https://en.wikipedia.org/wiki/Hemodialysis' "
            "target='_blank'>dialysis</a>?",
        )
        self.fields["dialysis_duration"].help_text = _(
            f"How long since {self.str_attrs['subject_the']} "  # noqa: INT001
            "started dialysis?",
        )
        self.fields["stage"].help_text = mark_safe(  # noqa: S308
            "What stage CKD? "
            f"If unsure, but {self.str_attrs['subject_the_pos']}"
            " <a class='samepage-link' href=#baselinecreatinine>"
            "baseline creatinine</a> is known, enter "
            "it below and GoutHelper will calculate the stage.",
        )
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "",
                Div(
                    Div(
                        Div(
                            Div(
                                Div(
                                    Field("dialysis"),
                                    css_class="col",
                                ),
                                css_class="row",
                                css_id="dialysis",
                            ),
                            Div(
                                Div(
                                    "dialysis_type",
                                    css_class="col",
                                ),
                                css_class="row",
                                css_id="dialysis_type",
                            ),
                            Div(
                                Div(
                                    "dialysis_duration",
                                    css_class="col",
                                ),
                                css_class="row",
                                css_id="dialysis_duration",
                            ),
                            css_id="dialysis-subform",
                        ),
                        Div(
                            Div(
                                "stage",
                                css_class="col",
                            ),
                            css_class="row",
                            css_id="stage",
                        ),
                        Div(
                            Div(
                                Div(
                                    HTML(
                                        """
                                        {% load crispy_forms_tags %}
                                        {% crispy baselinecreatinine_form %}
                                        """,
                                    ),
                                    css_class="col",
                                ),
                                css_class="row",
                            ),
                            css_id="baselinecreatinine",
                        ),
                        css_id="ckddetail",
                    ),
                    css_id="ckddetail-form",
                ),
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["dialysis"] is True:
            if cleaned_data["dialysis_type"] == "":
                self.add_error(
                    "dialysis_type",
                    ValidationError(
                        "If dialysis is checked, dialysis type is required.",
                        code="dialysis_type",
                    ),
                )
            if cleaned_data["dialysis_duration"] == "":
                self.add_error(
                    "dialysis_duration",
                    ValidationError(
                        ("If dialysis is checked, dialysis duration is required."),
                        code="dialysis_duration",
                    ),
                )
            if cleaned_data["stage"] is not Stages.FIVE:
                cleaned_data.update({"stage": Stages.FIVE})
        else:
            if cleaned_data["dialysis_type"] is not None:
                cleaned_data.update({"dialysis_type": None})
            if cleaned_data["dialysis_duration"] is not None:
                cleaned_data.update({"dialysis_duration": None})
        return cleaned_data
