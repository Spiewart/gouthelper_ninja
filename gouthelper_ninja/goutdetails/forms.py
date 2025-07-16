from django.forms import TypedChoiceField
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from gouthelper_ninja.choices import BOOL_CHOICES
from gouthelper_ninja.choices import YES_OR_NO_OR_NONE
from gouthelper_ninja.choices import YES_OR_NO_OR_UNKNOWN
from gouthelper_ninja.goutdetails.models import GoutDetail
from gouthelper_ninja.utils.forms import GoutHelperForm
from gouthelper_ninja.utils.forms import coerce_form_input_to_bool
from gouthelper_ninja.utils.forms import coerce_form_input_to_bool_or_none


class GoutDetailForm(GoutHelperForm):
    model = GoutDetail

    at_goal = TypedChoiceField(
        label=_("Goal Uric Acid"),
        choices=YES_OR_NO_OR_UNKNOWN,
        coerce=coerce_form_input_to_bool_or_none,
        help_text=_(
            "Is the patient at goal uric acid? Goal is typically < 6.0 mg/dL.",
        ),
        initial=None,
        required=True,
    )
    at_goal_long_term = TypedChoiceField(
        label=_("At Goal Six Months or Longer"),
        choices=BOOL_CHOICES,
        coerce=coerce_form_input_to_bool,
        help_text=_(
            "Has the patient been at goal uric acid six months or longer? "
            "Goal is typically < 6.0 mg/dL.",
        ),
        initial=False,
    )
    flaring = TypedChoiceField(
        label=_("Flaring"),
        choices=YES_OR_NO_OR_UNKNOWN,
        coerce=coerce_form_input_to_bool_or_none,
        help_text=_("Has the patient had a recent gout flare?"),
        initial=None,
        required=False,
    )
    on_ppx = TypedChoiceField(
        label=_("On Prophylaxis"),
        choices=YES_OR_NO_OR_NONE,
        coerce=coerce_form_input_to_bool,
        help_text=_("Is the patient on gout prophylaxis?"),
        initial=False,
        required=False,
    )
    on_ult = TypedChoiceField(
        label=_("On ULT"),
        choices=YES_OR_NO_OR_NONE,
        coerce=coerce_form_input_to_bool,
        empty_value=None,
        help_text=_("Is the patient on urate lowering therapy?"),
        initial=False,
        required=False,
    )
    starting_ult = TypedChoiceField(
        label=_("Starting ULT"),
        choices=YES_OR_NO_OR_NONE,
        coerce=coerce_form_input_to_bool,
        empty_value=None,
        help_text=_(
            "Is the patient starting urate lowering therapy? "
            "This is typically used when starting a new patient on ULT.",
        ),
        initial=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        at_goal = cleaned_data.get("at_goal", None)
        at_goal_long_term = cleaned_data.get("at_goal_long_term", None)
        if at_goal_long_term is True and at_goal is False:
            self.add_error(
                "at_goal",
                ValidationError(
                    (
                        "If at goal long term, "
                        "the patient must be at goal uric acid level."
                    ),
                    code="at_goal",
                ),
            )
        return cleaned_data
