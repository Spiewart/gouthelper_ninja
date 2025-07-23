from typing import TYPE_CHECKING
from typing import Any
from typing import Literal

from django.views.generic import UpdateView

from gouthelper_ninja.genders.forms import GenderForm
from gouthelper_ninja.genders.models import Gender
from gouthelper_ninja.utils.views import GoutHelperEditMixin
from gouthelper_ninja.utils.views import GoutHelperUpdateMixin
from gouthelper_ninja.utils.views import PatientObjectMixin

if TYPE_CHECKING:
    from gouthelper_ninja.genders.choices import Genders


class GenderEditMixin(GoutHelperEditMixin):
    """Mixin for updating Genders."""

    model = Gender
    form_class = GenderForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.model is not Gender and "gender_form" not in context:
            context["gender_form"] = GenderForm(
                initial=self.get_gender_initial(),
                **self.subform_kwargs,
            )

        return context

    def get_gender_initial(self) -> dict[Literal["gender"], "Genders"]:
        """Return initial data for the Gender form."""
        if self.patient and hasattr(self.patient, "gender"):
            return {"gender": self.patient.gender.gender}
        return {}

    def post_init(self) -> None:
        """Overwritten to add the GenderForm to the kwargs if
        the model is not Gender."""
        if self.model is not Gender:
            self.forms["gender_form"] = GenderForm(
                initial=self.get_gender_initial(),
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
