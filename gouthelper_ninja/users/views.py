from typing import TYPE_CHECKING
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.http import Http404
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from rules.contrib.views import AutoPermissionRequiredMixin
from rules.contrib.views import PermissionRequiredMixin

from gouthelper_ninja.dateofbirths.views import DateOfBirthEditMixin
from gouthelper_ninja.ethnicitys.views import EthnicityEditMixin
from gouthelper_ninja.genders.views import GenderEditMixin
from gouthelper_ninja.medhistorys.views import GoutMixin
from gouthelper_ninja.users.forms import PatientForm
from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.models import User
from gouthelper_ninja.users.querysets import patient_qs
from gouthelper_ninja.users.schema import PatientSchema
from gouthelper_ninja.utils.views import GoutHelperCreateMixin
from gouthelper_ninja.utils.views import GoutHelperUpdateMixin

if TYPE_CHECKING:
    from pydantic import BaseModel


class PatientEditMixin(
    DateOfBirthEditMixin,
    EthnicityEditMixin,
    GenderEditMixin,
    GoutMixin,
):
    """Mixin adding common elements for editing a Patient,
    including date of birth, ethnicity, and gender."""

    form_class = PatientForm


class PatientCreateView(
    PatientEditMixin,
    GoutHelperCreateMixin,
    CreateView,
):
    """View for creating new Patients with their associated profile,
    date of birth, ethnicity, and gender.

    TODO: Add required MedHistorys (i.e. menopause as needed) once
    this app is implemented."""

    model = Patient

    @cached_property
    def patient(self) -> None:
        """Returns None, as this view is for creating a new Patient."""
        return


class PatientProviderCreateView(
    PermissionRequiredMixin,
    PatientCreateView,
):
    permission_required = "users.can_add_provider_patient"

    def dispatch(self, request, *args, **kwargs):
        """Overwritten to check if the provider kwarg belongs to a
        User who exists, and if not, raises a 404 error."""
        try:
            self.provider  # noqa: B018
        except User.DoesNotExist as e:
            raise Http404(
                _("No provider found with username: %(username)s")
                % {"username": self.kwargs.get("provider", "unknown")},
            ) from e
        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    @cached_property
    def provider(self) -> User:
        """Returns the provider User object specified by the
        provider_id URL kwarg. Can be overwritten by child classes
        to select_related or prefetch_related models required
        for the view."""

        return User.objects.get(
            username=self.kwargs.get("provider"),
        )

    def get_permission_object(self) -> str | None:
        """Need to return the provider kwarg as the permission object,
        if passed by the URL, to check permission for creating a Patient
        for that provider. If not passed, returns None."""

        return self.kwargs.get("provider", None)

    def create_object(
        self,
        schema: "BaseModel",
        **kwargs: dict[str, Any],
    ) -> Patient:
        """Overwritten to create a Patient with the provider_id
        passed in the kwargs, which is required for creating a
        Patient for a provider."""
        kwargs.update(
            {
                "provider_id": self.provider.id,
            },
        )
        return super().create_object(schema, **kwargs)


class PatientMixin:
    """Mixin for handling a Patient object in views."""

    model = Patient

    @cached_property
    def patient(self) -> Patient:
        """Returns the Patient object being updated."""
        return (
            self.object if hasattr(self, "object") else self.get_object()  # type: ignore[return-value,attr-defined]
        )

    def dispatch(self, request, *args, **kwargs):
        """Overwritten to set the object attribute on the view,
        which is used by the patient cached_property, which is
        then used to check object-level permissions."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None) -> Patient | None:
        """Overwritten to use the patient kwarg rather than pk or
        slug to get the Patient object. Also, checks if the object
        is already set on the view, and returns it if so to avoid
        duplicate database queries and still work with Django CBVs
        without re-writing several methods."""
        if not hasattr(self, "object"):
            if queryset is None:
                queryset = self.get_queryset()
            patient_id = self.kwargs.get("patient", None)
            if patient_id is None:
                class_name = self.__class__.__name__
                raise AttributeError(
                    class_name
                    + " must be called with a Patient uuid in the patient kwarg "
                    "in the URLconf.",
                )
            queryset = queryset.filter(
                pk=patient_id,
            )
            try:
                obj = queryset.get()
            except queryset.model.DoesNotExist as e:
                raise Http404(
                    _("No %(verbose_name)s found matching the query")
                    % {"verbose_name": queryset.model._meta.verbose_name},  # noqa: SLF001
                ) from e
        else:
            obj = self.object
        return obj

    def get_permission_object(self) -> User:
        """Returns the Patient object that is being updated,
        which is used to check permissions for updating the Patient."""
        return self.patient

    def get_queryset(self) -> QuerySet[Patient]:
        """Returns the queryset with the necessary related models
        for updating select_related and prefetch_related."""
        return patient_qs(super().get_queryset())


class PatientDeleteView(
    AutoPermissionRequiredMixin,
    SuccessMessageMixin,
    PatientMixin,
    DeleteView,
):
    """View for deleting a Patient.
    Only authenticated users can delete a Patient.
    Permission via rules."""

    # TODO: when session management is implemented,
    # TODO: remove the patient from the session in form_valid

    def get_success_message(self, cleaned_data):
        return _("GoutPatient successfully deleted")

    def get_success_url(self):
        # If the user is deleting their own account, redirect to home.
        # The user will be logged out after this.
        if self.request.user.pk == self.object.pk:
            return reverse("contents:home")
        return reverse("users:detail", kwargs={"username": self.request.user.username})


class PatientDetailView(
    AutoPermissionRequiredMixin,
    PatientMixin,
    DetailView,
):
    """View for displaying a Patient's details."""


class PatientUpdateView(
    PatientMixin,
    PatientEditMixin,
    GoutHelperUpdateMixin,
    AutoPermissionRequiredMixin,
    UpdateView,
):
    """View for updating existing Patients with their associated profile,
    date of birth, ethnicity, and gender.

    TODO: Add required MedHistorys (i.e. menopause as needed) once
    this app is implemented."""

    schema = PatientSchema

    def create_schema(self, data: dict[str, Any]) -> "BaseModel":
        """Overwritten to add the Patient's id to the schema data,
        which is required for the schema validation."""
        data.update(
            {"id": str(self.patient.id)},
        )
        return super().create_schema(data)


# TODO: use Django-rules to prevent accessing User views for Patients
# TODO: that are not the request user.


class UserDeleteView(
    LoginRequiredMixin,
    AutoPermissionRequiredMixin,
    SuccessMessageMixin,
    DeleteView,
):
    model = User
    # template_name needs to be declared because a User proxy model
    # will have a different model name and Django will not find the
    # correct template.
    template_name = "users/user_confirm_delete.html"

    def get_success_message(self, cleaned_data):
        return _("Account successfully deleted")

    def get_success_url(self):
        return reverse("contents:home")

    def get_object(self):
        return self.request.user


user_delete_view = UserDeleteView.as_view()


class UserDetailView(LoginRequiredMixin, AutoPermissionRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(
    LoginRequiredMixin,
    AutoPermissionRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
