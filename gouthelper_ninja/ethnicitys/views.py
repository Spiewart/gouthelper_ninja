from typing import Any

from django.views.generic import UpdateView

from gouthelper_ninja.ethnicitys.forms import EthnicityForm
from gouthelper_ninja.ethnicitys.models import Ethnicity
from gouthelper_ninja.utils.views import GoutHelperEditMixin
from gouthelper_ninja.utils.views import GoutHelperUpdateMixin
from gouthelper_ninja.utils.views import PatientObjectMixin


class EthnicityEditMixin(GoutHelperEditMixin):
    """Mixin for updating Ethnicitys."""

    model = Ethnicity
    form_class = EthnicityForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.model is not Ethnicity and "ethnicity_form" not in context:
            context["ethnicity_form"] = EthnicityForm(
                initial={"ethnicity": self.patient.ethnicity.ethnicity}
                if self.patient
                else {},
                **self.subform_kwargs,
            )

        return context

    def post_init(self) -> None:
        """Overwritten to add the EthnicityForm to the kwargs if
        the model is not Ethnicity."""

        if self.model is not Ethnicity:
            self.forms["ethnicity_form"] = EthnicityForm(
                initial={"ethnicity": self.patient.ethnicity.ethnicity}
                if self.patient
                else {},
                data=self.request.POST,
                **self.subform_kwargs,
            )
        super().post_init()


class EthnicityUpdateView(
    # PatientObjectMixin needs to be first so it sets self.patient
    PatientObjectMixin,
    GoutHelperUpdateMixin,
    EthnicityEditMixin,
    UpdateView,
):
    """View for updating a Patient's Ethnicity."""
