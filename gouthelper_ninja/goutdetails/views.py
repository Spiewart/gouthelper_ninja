from typing import TYPE_CHECKING
from typing import Any

from django.views.generic import UpdateView

from gouthelper_ninja.goutdetails.forms import GoutDetailForm
from gouthelper_ninja.goutdetails.models import GoutDetail
from gouthelper_ninja.utils.views import GoutHelperEditMixin
from gouthelper_ninja.utils.views import GoutHelperUpdateMixin
from gouthelper_ninja.utils.views import PatientObjectMixin

if TYPE_CHECKING:
    from django.db.models import Model
    from django.forms import Form


class GoutDetailEditMixin(GoutHelperEditMixin):
    """Mixin for updating GoutDetails."""

    model: type["Model"] = GoutDetail
    form_class: type["Form"] = GoutDetailForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.model is not GoutDetail and "goutdetail_form" not in context:
            context["goutdetail_form"] = GoutDetailForm(
                initial=self.get_goutdetail_initial(),
                **self.subform_kwargs,
            )

        return context

    def get_goutdetail_initial(self) -> dict[str, Any]:
        """Returns the initial data for the GoutDetailForm."""
        return (
            {
                "at_goal": self.patient.goutdetail.at_goal,
                "at_goal_long_term": self.patient.goutdetail.at_goal_long_term,
                "flaring": self.patient.goutdetail.flaring,
                "on_ppx": self.patient.goutdetail.on_ppx,
                "on_ult": self.patient.goutdetail.on_ult,
                "starting_ult": self.patient.goutdetail.starting_ult,
            }
            if self.patient
            else {}
        )

    def post_init(self) -> None:
        """Overwritten to add the GoutDetailForm to the kwargs if
        the model is not GoutDetail."""
        if self.model is not GoutDetail:
            self.forms["goutdetail_form"] = GoutDetailForm(
                initial=self.get_goutdetail_initial(),
                data=self.request.POST,
                **self.subform_kwargs,
            )
        super().post_init()


class GoutDetailUpdateView(
    # PatientObjectMixin needs to be first so it sets self.patient
    PatientObjectMixin,
    GoutHelperUpdateMixin,
    GoutDetailEditMixin,
    UpdateView,
):
    """View for updating a Patient's GoutDetail."""
