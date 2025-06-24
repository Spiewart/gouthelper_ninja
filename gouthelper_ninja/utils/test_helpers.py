import logging
from typing import TYPE_CHECKING
from typing import Union

from django.forms import BaseModelFormSet

from gouthelper_ninja.utils.helpers import get_str_attrs_dict

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.http import HttpResponse

    from gouthelper_ninja.users.models import Patient
    from gouthelper_ninja.users.models import User


RESPONSE_REDIRECT = 302
RESPONSE_SUCCESS = 200
RESPONSE_UNAUTHORIZED = 401
RESPONSE_FORBIDDEN = 403
RESPONSE_NOT_FOUND = 404
RESPONSE_UNPROCESSABLE_CONTENT = 422


def create_form_kwargs(
    patient: Union["Patient", "User", None] = None,
    request_user: Union["User", None] = None,
    str_attrs: dict[str, str] | None = None,
) -> dict[str, Union["Patient", "User", dict[str, str]]]:
    """Create kwargs for GoutHelper forms."""
    kwargs = {
        "patient": patient,
        "request_user": request_user,
    }
    if not str_attrs:
        kwargs["str_attrs"] = get_str_attrs_dict(
            patient=patient,
            request_user=request_user,
        )
    return kwargs


def dummy_get_response(request: "HttpRequest"):
    return None


def print_response_errors(response: Union["HttpResponse", None] = None) -> None:
    """Used to troubleshoot View testing: print errors for all forms and formsets
    in the context_data."""

    if response and hasattr(response, "context_data"):
        for key, val in response.context_data.items():
            if key.endswith("_form") or key == "form":
                if getattr(val, "errors", None):
                    logging.error("printing form errors: %s - %s", key, val.errors)
            elif val and isinstance(val, BaseModelFormSet):
                non_form_errors = val.non_form_errors()
                if non_form_errors:
                    logging.error(
                        "printing non form errors: %s - %s",
                        key,
                        non_form_errors,
                    )
                # Check if the formset has forms and iterate over them if so
                if val.forms:
                    for form in val.forms:
                        if getattr(form, "errors", None):
                            logging.error(
                                "printing formset form errors: %s - %s",
                                key,
                                form.errors,
                            )
                            logging.error(form.instance.pk)
                            logging.error(form.instance.date_drawn)
                            logging.error(form.instance.value)
