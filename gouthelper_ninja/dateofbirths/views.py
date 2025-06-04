from typing import Any

from gouthelper_ninja.dateofbirths.forms import DateOfBirthForm
from gouthelper_ninja.dateofbirths.models import DateOfBirth
from gouthelper_ninja.dateofbirths.schema import DateOfBirthNestedSchema
from gouthelper_ninja.utils.views import GoutHelperEditMixin
from gouthelper_ninja.utils.views import GoutHelperUpdateMixin


class DateOfBirthEditMixin(GoutHelperEditMixin):
    """Mixin for updating DateOfBirths."""

    model = DateOfBirth
    form_class = DateOfBirthForm
    schema = DateOfBirthNestedSchema

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.model is not DateOfBirth and "dateofbirth_form" not in context:
            context["dateofbirth_form"] = DateOfBirthForm(
                initial={"dateofbirth": self.patient.dateofbirth.dateofbirth}
                if self.patient
                else {},
                **self.subform_kwargs,
            )
        return context

    def post_init(self) -> None:
        """Overwritten to add the DateOfBirthForm to the kwargs if
        the model is not DateOfBirth."""
        if self.model is not DateOfBirth:
            self.forms["dateofbirth_form"] = DateOfBirthForm(
                initial={"dateofbirth": self.patient.dateofbirth.dateofbirth}
                if self.patient
                else {},
                data=self.request.POST,
                **self.subform_kwargs,
            )
        super().post_init()


class DateOfBirthUpdateView(GoutHelperUpdateMixin, DateOfBirthEditMixin):
    """View for updating a Patient's DateOfBirth."""
