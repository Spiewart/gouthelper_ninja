from django.forms import BooleanField
from django.utils.translation import gettext_lazy as _

from gouthelper_ninja.goutdetails.models import GoutDetail
from gouthelper_ninja.utils.forms import GoutHelperForm


class GoutDetailForm(GoutHelperForm):
    model = GoutDetail

    at_goal = BooleanField(
        label=_("Goal Uric Acid"),
        help_text=_(
            "Is the patient at goal uric acid? Goal is typically < 6.0 mg/dL.",
        ),
        initial=None,
    )
    at_goal_long_term = BooleanField(
        label=_("At Goal Six Months or Longer"),
        help_text=_(
            "Has the patient been at goal uric acid six months or longer? "
            "Goal is typically < 6.0 mg/dL.",
        ),
        initial=False,
    )
    flaring = BooleanField(
        label=_("Flaring"),
        help_text=_("Has the patient had a recent gout flare?"),
        initial=None,
    )
    on_ppx = BooleanField(
        label=_("On Prophylaxis"),
        help_text=_("Is the patient on gout prophylaxis?"),
        initial=False,
    )
    on_ult = BooleanField(
        label=_("On ULT"),
        help_text=_("Is the patient on urate lowering therapy?"),
        initial=False,
    )
    starting_ult = BooleanField(
        label=_("Starting ULT"),
        help_text=_(
            "Is the patient starting urate lowering therapy? "
            "This is typically used when starting a new patient on ULT.",
        ),
        initial=False,
    )
