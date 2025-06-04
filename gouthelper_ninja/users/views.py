from typing import TYPE_CHECKING
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from gouthelper_ninja.dateofbirths.views import DateOfBirthEditMixin
from gouthelper_ninja.ethnicitys.views import EthnicityEditMixin
from gouthelper_ninja.genders.views import GenderEditMixin
from gouthelper_ninja.users.forms import PatientCreateForm
from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.models import User
from gouthelper_ninja.users.schema import PatientCreateSchema
from gouthelper_ninja.utils.views import GoutHelperCreateMixin

if TYPE_CHECKING:
    from pydantic import BaseModel


class PatientCreateView(
    DateOfBirthEditMixin,
    EthnicityEditMixin,
    GenderEditMixin,
    GoutHelperCreateMixin,
    SuccessMessageMixin,
):
    """View for creating new Patients with their associated profile,
    date of birth, ethnicity, and gender.

    TODO: Add required MedHistorys (i.e. menopause as needed) once
    this app is implemented."""

    model = Patient
    form_class = PatientCreateForm
    schema = PatientCreateSchema

    @cached_property
    def patient(self) -> None:
        """Overwritten to return None, as the patient is not
        created until the form is submitted."""
        return

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

    def get_permission_object(self):
        """The view's permission_object is the provider, which is used
        to check permissions for creating a Patient for that provider."""

        return self.provider

    def create_schema(self, data: dict[str, Any]) -> "BaseModel":
        """Overwritten to add the provider to the schema."""

        data["provider"] = str(self.provider.id) if self.provider else None
        return super().create_schema(data)


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
