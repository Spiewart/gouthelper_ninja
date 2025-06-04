import logging
from typing import TYPE_CHECKING
from typing import Union

from django.forms import BaseModelFormSet

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.http import HttpResponse


RESPONSE_REDIRECT_STATUS = 302
RESPONSE_STATUS = 200


def dummy_get_response(request: "HttpRequest"):
    return None


def print_response_errors(response: Union["HttpResponse", None] = None) -> None:
    """Used to troubleshoot View testing: print errors for all forms and formsets
    in the context_data."""

    if response and hasattr(response, "context_data"):
        for key, val in response.context_data.items():
            if key.endswith("_form") or key == "form":
                if getattr(val, "errors", None):
                    logging.error("printing form errors")
                    logging.error(key, val.errors)
            elif val and isinstance(val, BaseModelFormSet):
                non_form_errors = val.non_form_errors()
                if non_form_errors:
                    logging.error("printing non form errors")
                    logging.error(key, non_form_errors)
                # Check if the formset has forms and iterate over them if so
                if val.forms:
                    for form in val.forms:
                        if getattr(form, "errors", None):
                            logging.error("printing formset form errors")
                            logging.error("printing formset form errors")
                            logging.error(form.instance.pk)
                            logging.error(form.instance.date_drawn)
                            logging.error(form.instance.value)
                            logging.error(key, form.errors)
