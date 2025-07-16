from typing import TYPE_CHECKING
from typing import Any
from typing import Union

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_htmx.http import HttpResponseClientRefresh
from pydantic import ValidationError as PydanticValidationError
from rules.contrib.views import AutoPermissionRequiredMixin

from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.utils.helpers import get_str_attrs_dict
from gouthelper_ninja.utils.models import GetStrAttrsMixin

if TYPE_CHECKING:
    from django.db.models import Model
    from django.http import HttpRequest
    from pydantic import BaseModel

    from gouthelper_ninja.users.models import User
    from gouthelper_ninja.utils.forms import GoutHelperForm


class GoutHelperEditMixin(SuccessMessageMixin, GetStrAttrsMixin):
    request: "HttpRequest"
    form_class: "GoutHelperForm"
    model: "Model"
    patient: Union["User", "Patient", None]

    def get_permission_object(self):
        """The view's permission_object is the patient, which is either an attribute
        of the view's object or derived from the view's patient kwarg."""

        return self.patient

    def get_form_kwargs(self):
        """Overwritten to avoid adding "instance" to the kwargs, which is not needed
        for the form, as it is not a ModelForm."""

        kwargs = {
            "initial": self.get_initial(),
            "prefix": self.get_prefix(),
        }
        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                },
            )
        kwargs.update(**self.subform_kwargs)
        return kwargs

    def get_initial(self) -> dict[str, Any]:
        """Overwritten to add initial data to the form. If the view's object is set,
        it will populate the initial data with the object's fields, if they are
        not already in the initial data."""

        initial = super().get_initial()

        if self.object:
            obj_field_names = [
                field.name
                for field in self.object._meta.get_fields()  # noqa: SLF001
            ]
            for field in self.model.edit_schema.model_fields:
                if field in initial:
                    continue
                if field in obj_field_names:
                    obj_field_names.remove(field)
                    # If the field is a model field, get its value from the object
                    initial[field] = getattr(self.object, field)
        return initial

    @property
    def subform_kwargs(self) -> dict[str, Any]:
        return {
            "patient": self.patient,
            "request_user": self.request_user,
            "str_attrs": self.str_attrs,
        }

    @cached_property
    def str_attrs(self) -> dict[str, str]:
        """Returns the str_attrs attribute on the object as a dictionary of
        {str: str} key/vals to allow fetching context-specific strings for
        display language."""
        return get_str_attrs_dict(
            patient=self.patient,
            request_user=self.request_user,
        )

    @cached_property
    def request_user(self) -> "User":
        """Returns the user who made the request."""
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.forms: dict[str, GoutHelperForm] = {}
        self.post_init()
        if self.post_forms_valid():
            self.post_process_forms()
        else:
            self.errors = self.render_errors(
                errors_context=self.form_errors_context(),
            )

        if self.errors:
            # If there are form errors, render them
            return self.errors

        data = {}
        for form in self.forms.values():
            if form.model != self.model:
                data.update(
                    {
                        form.model.__name__.lower(): form.cleaned_data,
                    },
                )
            else:
                data.update(form.cleaned_data)
        try:
            schema = self.create_schema(data)
        except PydanticValidationError as e:
            # If the schema validation fails, we catch the error
            self.errors = self.render_errors(
                errors_context=self.schema_errors_context(
                    schema_errors=e.errors(),
                ),
            )

        if self.errors:
            return self.errors

        return self.form_valid(schema=schema, **kwargs)

    def post_init(self) -> None:
        """Method that initializes the forms and formsets for the view's
        post() method in a dictionary.
        Overwritten by child classes to add additional forms and formsets."""

        self.forms["form"] = self.get_form_class()(
            **self.get_form_kwargs(),
        )

    def post_forms_valid(self) -> bool:
        """Validates all forms in the view's forms dictionary."""
        forms_valid = True

        for form in self.forms.values():
            forms_valid = form.is_valid() and forms_valid
        return forms_valid

    def post_process_forms(self) -> None:
        """Parent method for child classes to inherit.
        super() will be called in the child class."""
        # Can process for post errors and set self.errors to self.render_errors()
        self.errors = False

    def render_errors(self, errors_context: dict[str, Any]) -> "HttpResponse":
        """Renders forms with errors in multiple locations in post()."""

        return self.render_to_response(
            context=errors_context,
        )

    def form_errors_context(self) -> dict[str, Any]:
        """To be overwritten by child classes to add additional
        forms to the errors context."""
        return self.get_context_data(
            **self.forms,
        )

    def create_schema(self, data: dict[str, Any]) -> "BaseModel":
        """Method that creates the View's Pydantic schema from the schema
        attribute using the data passed in. Can be overwritten in child classes
        for additional functionality or processing."""

        try:
            return self.model.edit_schema(**data)
        except PydanticValidationError as e:
            # If the schema validation fails, we catch the error
            raise e from PydanticValidationError(
                _(f"{self.model.edit_schema.__name__} validation failed."),  # noqa: INT001
            )

    def schema_errors_context(
        self,
        schema_errors: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Adds Pydantic schema ValidationErrors to the context data
        for rendering a 200 error response."""

        # TODO: figure out how to render the schema errors in the correct forms

        return {}

    def form_valid(
        self,
        schema: "BaseModel",
        **kwargs: dict[str, Any],
    ) -> "HttpResponse":
        """Overwritten to turn take a validated pydantic schema to be
        used as args for create/update methods. Returns typical
        HttpResponseRedirect if successful, or HTMX response if
        the request is HTMX."""

        # Requires object be set by child views
        messages.success(
            self.request,
            self.get_success_message(self.forms["form"].cleaned_data),
        )
        if self.request.htmx:
            return self.get_htmx_response()
        return HttpResponseRedirect(self.get_success_url())

    def get_htmx_response(self) -> HttpResponseClientRefresh:
        """Generates an HTMX response. Default is to refresh the page,
        but can be overwritten in child classes to return a different
        HTMX response."""
        return HttpResponseClientRefresh()


class PatientKwargMixin:
    """Mixin for CRUD views that have a patient kwarg in the URL.
    Fetches the Patient and adds to the context and the object
    creation method. MUST BE FIRST IN THE MRO."""

    @cached_property
    def patient(self) -> "User":
        """Returns the Patient whose pk is equal to the patient kwarg,
        which is passed in the URL."""

        return (
            Patient.objects.select_related(
                "patientprofile__provider",
            )
            .filter(pk=self.kwargs.get("patient"))
            .get()
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Overwritten to add the patient to the context data."""
        context = super().get_context_data(**kwargs)
        context["patient"] = self.patient
        return context

    def create_object(
        self,
        schema: "BaseModel",
        **kwargs: dict[str, Any],
    ) -> "Patient":
        """Overwritten to create a Patient with the patient kwarg
        passed in the URL, which is required for creating a Patient."""
        kwargs.update(
            {
                "patient_id": self.patient.id,
            },
        )
        return super().create_object(schema, **kwargs)


class PatientObjectMixin(AutoPermissionRequiredMixin):
    """Mixin for handling objects that have a OneToOne relationship
    with a Patient via a patient field. MUST BE FIRST IN MRO.
    Patient used to set the object on dispatch, which is then used to
    check object-level permissions. get_object() can be called multiple
    times without re-querying the database if the object is already set on the view."""

    object: Any

    @cached_property
    def patient(self) -> "User":
        """Returns the view's object's patient."""
        return self.object.patient

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
            pk = self.kwargs.get("pk", None)
            if pk is None:
                class_name = self.__class__.__name__
                raise AttributeError(
                    class_name + " must be called with a uuid in the pk kwarg "
                    "in the URLconf.",
                )
            queryset = queryset.filter(
                pk=pk,
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


class GoutHelperCreateMixin(GoutHelperEditMixin):
    def post(self, request, *args, **kwargs):
        """Overwritten to set the patient attribute on the view."""
        self.object = None

        return super().post(request, *args, **kwargs)

    def form_valid(self, schema: "BaseModel", **kwargs) -> "HttpResponse":
        """Overwritten to turn take a validated pydantic schema to be
        used as args for create/update methods. Returns typical
        HttpResponseRedirect if successful, or HTMX response if
        the request is HTMX."""

        self.object = self.create_object(schema)
        return super().form_valid(schema=schema, **kwargs)

    def create_object(self, schema: "BaseModel", **kwargs: dict[str, Any]) -> "Model":
        """Method to create the object from the validated schema.
        Can be overwritten in child classes to add additional
        functionality or processing."""

        return self.model.objects.gh_create(data=schema, **kwargs)


class GoutHelperUpdateMixin(GoutHelperEditMixin):
    def post(self, request, *args, **kwargs):
        """Overwritten to set the patient attribute on the view."""
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, schema: "BaseModel", **kwargs) -> "HttpResponse":
        """Overwritten to turn take a validated pydantic schema to be
        used as args for create/update methods. Returns typical
        HttpResponseRedirect if successful, or HTMX response if
        the request is HTMX."""
        self.object = self.object.update(data=schema)
        return super().form_valid(schema=schema, **kwargs)
