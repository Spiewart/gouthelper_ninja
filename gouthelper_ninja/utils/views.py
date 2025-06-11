from typing import TYPE_CHECKING
from typing import Any
from typing import Union

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.functional import cached_property

from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.utils.helpers import get_str_attrs_dict
from gouthelper_ninja.utils.models import GetStrAttrsMixin

if TYPE_CHECKING:
    from django.db.models import Model
    from django.forms import Form
    from django.http import HttpRequest
    from pydantic import BaseModel

    from gouthelper_ninja.users.models import User


class GoutHelperEditMixin(SuccessMessageMixin, GetStrAttrsMixin):
    request: "HttpRequest"
    form_class: "Form"
    model: "Model"
    patient: Union["User", "Patient", None]
    schema: "BaseModel"

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
            for field in self.schema.model_fields:
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
        self.forms: dict[str, Form] = {}
        self.post_init()
        if self.post_forms_valid():
            self.post_process_forms()
        else:
            self.errors = self.render_errors(**kwargs)

        if self.errors:
            return self.errors

        data = {}
        for form in self.forms.values():
            data.update(form.cleaned_data)

        schema = self.create_schema(data)

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

    def render_errors(self) -> "HttpResponse":
        """Renders forms with errors in multiple locations in post()."""
        context = self.get_errors_context()
        return self.render_to_response(
            self.get_context_data(
                **context,
            ),
        )

    def get_errors_context(self) -> dict[str, Any]:
        """To be overwritten by child classes to add additional
        forms to the errors context."""
        return self.get_context_data(
            **self.forms,
        )

    def create_schema(self, data: dict[str, Any]) -> "BaseModel":
        """Method that creates the View's Pydantic schema from the schema
        attribute using the data passed in. Can be overwritten in child classes
        for additional functionality or processing."""
        return self.schema(**data)

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
            return kwargs.get("htmx")
        return HttpResponseRedirect(self.get_success_url())


class PatientKwargMixin:
    @cached_property
    def patient(self) -> "User":
        """Returns the Patient whose pk is equal to the patient kwarg,
        which is passed in the URL."""

        return Patient.objects.filter(pk=self.kwargs.get("patient")).get()


class PatientObjectMixin:
    object: Any

    @cached_property
    def patient(self) -> "User":
        """Returns the view's object's patient."""
        return self.object.patient


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

        self.object = self.model.objects.create(**schema.dict())
        return super().form_valid(schema=schema, **kwargs)


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

        self.object = self.object.update(**schema.dict())
        return super().form_valid(schema=schema, **kwargs)
