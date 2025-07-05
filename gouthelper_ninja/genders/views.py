from typing import Any

from django.views.generic import UpdateView

from gouthelper_ninja.genders.forms import GenderForm
from gouthelper_ninja.genders.models import Gender
from gouthelper_ninja.utils.views import GoutHelperEditMixin
from gouthelper_ninja.utils.views import GoutHelperUpdateMixin
from gouthelper_ninja.utils.views import PatientObjectMixin


class GenderEditMixin(GoutHelperEditMixin):
    """Mixin for updating Genders."""

    model = Gender
    form_class = GenderForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.model is not Gender and "gender_form" not in context:
            context["gender_form"] = GenderForm(
                initial={"gender": self.patient.gender.gender} if self.patient else {},
                **self.subform_kwargs,
            )

        return context

    def post_init(self) -> None:
        """Overwritten to add the GenderForm to the kwargs if
        the model is not Gender."""
        if self.model is not Gender:
            self.forms["gender_form"] = GenderForm(
                initial={"gender": self.patient.gender.gender} if self.patient else {},
                data=self.request.POST,
                **self.subform_kwargs,
            )
        super().post_init()


class GenderUpdateView(
    # PatientObjectMixin needs to be first so it sets self.patient
    PatientObjectMixin,
    GoutHelperUpdateMixin,
    GenderEditMixin,
    UpdateView,
):
    """View for updating a Patient's Gender."""
