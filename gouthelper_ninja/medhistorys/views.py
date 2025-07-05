from typing import Any

from django.apps import apps
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.generic import CreateView
from django.views.generic import UpdateView

from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.medhistorys.forms import MedHistoryForm
from gouthelper_ninja.medhistorys.models import MedHistory
from gouthelper_ninja.utils.views import GoutHelperCreateMixin
from gouthelper_ninja.utils.views import GoutHelperEditMixin
from gouthelper_ninja.utils.views import GoutHelperUpdateMixin
from gouthelper_ninja.utils.views import PatientKwargMixin
from gouthelper_ninja.utils.views import PatientObjectMixin


class MedHistoryMixin(GoutHelperEditMixin):
    form_class: type[MedHistoryForm] = MedHistoryForm
    mhtype: MHTypes
    template_name = "medhistorys/medhistory_form.html"

    @cached_property
    def model(self) -> type[MedHistory]:
        return apps.get_model("medhistorys", self.mh_name)

    @property
    def mh_name(self) -> str:
        """Returns the lowercase name of the MedHistory type."""
        return self.mhtype.name.lower()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Overwritten to add the mhtype to the context data."""
        context = super().get_context_data(**kwargs)
        context["mhtype"] = self.mhtype
        return context

    def get_form_kwargs(self) -> dict[str, Any]:
        """Overwritten to add the model and mhtype to the kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["model"] = self.model
        return kwargs


class MedHistoryCreateView(
    PatientKwargMixin,
    GoutHelperCreateMixin,
    MedHistoryMixin,
    CreateView,
):
    """View for creating a MedHistory."""

    @property
    def mhtype(self) -> MHTypes:
        try:
            return MHTypes(self.kwargs.get("mhtype"))
        except ValueError as e:
            msg = _(f"Invalid mhtype: {self.kwargs.get('mhtype')}.")  # noqa: INT001
            raise Http404(msg) from e

    def dispatch(self, request, *args, **kwargs):
        """Overwritten to check if the mhtype exists for the patient,
        redirects to the update view if it does."""
        # Get the model class based on the mhtype for the patient
        mh_id = self.model.objects.filter(
            patient=self.patient,
            mhtype=self.mhtype,
        ).values_list("pk", flat=True)
        if mh_id.exists():
            # Redirect to the update view if the MedHistory already exists
            return redirect(reverse("medhistorys:update", kwargs={"pk": mh_id.get()}))
        return super().dispatch(request, *args, **kwargs)


class MedHistoryUpdateView(
    PatientObjectMixin,
    GoutHelperUpdateMixin,
    MedHistoryMixin,
    UpdateView,
):
    """View for updating a MedHistory."""

    @property
    def mhtype(self) -> MHTypes:
        return MHTypes(self.object.mhtype)

    @property
    def model(self) -> type[MedHistory]:
        return (
            MedHistory
            if not hasattr(self, "object")
            else apps.get_model("medhistorys", self.mh_name)
        )


class MedHistoryProxyMixin(GoutHelperEditMixin):
    """Mixin for adding MedHistory proxy model(s) forms
    and processing to related object CRUD views. Child classes
    require calling update_context and post_init methods in
    their own get_context_data and post_init methods respectively."""

    def update_context(
        self,
        context: dict[str, Any],
        mhtype: MHTypes,
    ) -> dict[str, Any]:
        """Adds MedHistory forms to the context."""
        context.update(
            {
                f"{mhtype.name.lower()}_form": MedHistoryForm(
                    **self.get_mhform_kwargs(mhtype),
                ),
            },
        )
        return context

    def get_mhform_kwargs(self, mhtype: MHTypes, **kwargs) -> dict[str, Any]:
        """Returns kwargs for a MedHistoryForm based on the mhtype."""
        return {
            "model": apps.get_model("medhistorys", mhtype.name.lower()),
            "initial": self.get_mh_initial(mhtype),
            **kwargs,
            **self.subform_kwargs,
        }

    def get_mh_initial(self, mhtype: MHTypes) -> dict[str, Any]:
        """Returns initial data for the MedHistoryForm
        based on the mhtype."""
        mh = getattr(self.patient, mhtype.name.lower(), None)
        return (
            {
                "history_of": mh.history_of if mh else None,
            }
            if mh
            else {}
        )

    def update_forms(self, mhtype: MHTypes) -> None:
        """Updates the forms dictionary with the MedHistoryForm."""
        self.forms[f"{mhtype.name.lower()}_form"] = MedHistoryForm(
            **self.get_mhform_kwargs(mhtype),
            data=self.request.POST,
        )


class AnginaMixin(MedHistoryProxyMixin):
    """Mixin for editing Angina MedHistory."""

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        self.update_context(context, MHTypes.ANGINA)
        return context

    def post_init(self) -> None:
        self.update_forms(MHTypes.ANGINA)
        super().post_init()


class GoutMixin(MedHistoryProxyMixin):
    """Mixin for editing Gout MedHistory."""

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        self.update_context(context, MHTypes.GOUT)
        return context

    def post_init(self) -> None:
        self.update_forms(MHTypes.GOUT)
        super().post_init()
