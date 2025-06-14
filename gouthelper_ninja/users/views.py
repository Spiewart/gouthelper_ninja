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
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from rules.contrib.views import AutoPermissionRequiredMixin
from rules.contrib.views import PermissionRequiredMixin

from gouthelper_ninja.dateofbirths.views import DateOfBirthEditMixin
from gouthelper_ninja.ethnicitys.views import EthnicityEditMixin
from gouthelper_ninja.genders.views import GenderEditMixin
from gouthelper_ninja.users.forms import PatientForm
from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.models import User
from gouthelper_ninja.users.querysets import patient_update_qs
from gouthelper_ninja.users.schema import PatientCreateSchema
from gouthelper_ninja.users.schema import PatientUpdateSchema
from gouthelper_ninja.utils.views import GoutHelperCreateMixin
from gouthelper_ninja.utils.views import GoutHelperUpdateMixin

if TYPE_CHECKING:
    from pydantic import BaseModel


class PatientEditMixin(
    DateOfBirthEditMixin,
    EthnicityEditMixin,
    GenderEditMixin,
):
    """Mixin adding common elements for editing a Patient,
    including date of birth, ethnicity, and gender."""

    model = Patient
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

    schema = PatientCreateSchema

    @cached_property
    def patient(self) -> None:
        """Returns None, as this view is for creating a new Patient."""
        return


class PatientProviderCreateView(
    PermissionRequiredMixin,
    PatientCreateView,
):
    permission_required = "users.can_add_provider_patient"

    @cached_property
    def provider(self) -> User | None:
        """Returns the provider User object if the request user is
        the same as the provider specified in the URL kwargs.

        TODO: If other providers are ever able to create Patients
        for other providers, this will need to be updated to
        return the provider specified in the URL kwargs instead of
        the request user."""

        provider = self.kwargs.get("provider", None)

        return (
            self.request_user
            if provider and self.request_user.username == provider
            else None
        )

    def get_permission_object(self) -> str | None:
        """Need to return the provider kwarg as the permission object,
        if passed by the URL, to check permission for creating a Patient
        for that provider. If not passed, returns None."""

        return self.kwargs.get("provider", None)

    def create_schema(self, data: dict[str, Any]) -> "BaseModel":
        """Overwritten to add the provider to the schema."""

        data["provider"] = str(self.provider.id)
        return super().create_schema(data)


class PatientMixin:
    """Mixin for handling a Patient object in views."""

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
        return patient_update_qs(super().get_queryset())


class PatientDetailView(
    AutoPermissionRequiredMixin,
    PatientMixin,
    DetailView,
):
    """View for displaying a Patient's details."""

    model = Patient


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

    schema = PatientUpdateSchema


# TODO: use Django-rules to prevent accessing User views for Patients
# TODO: that are not the request user.


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
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
