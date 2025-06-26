from typing import TYPE_CHECKING

from django.apps import apps
from django.urls import reverse
from django.utils import timezone

from gouthelper_ninja.dateofbirths.querysets import annotate_patient_queryset_with_age
from gouthelper_ninja.users.querysets import age_gender_filter

if TYPE_CHECKING:
    from uuid import UUID

    from django.config.auth import get_user_model

    from gouthelper_ninja.genders.choices import Genders

    User = get_user_model()


def get_provider_alias(
    provider_id: "UUID",
    age: int,
    gender: "Genders",
) -> int | None:
    queryset = annotate_patient_queryset_with_age(
        qs=apps.get_model("users.Patient")
        .objects.select_related(
            "dateofbirth",
            "gender",
            "patientprofile__provider",
        )
        .filter(
            patientprofile__provider_id=provider_id,
            created__date=timezone.localdate(),
        ),
    )

    # Count of related patients with the same age, gender, and created date
    alias_conflicts = age_gender_filter(
        qs=queryset,
        age=age,
        gender=gender,
    ).count()

    return alias_conflicts + 1


def get_user_change(instance, request, **kwargs):  # pylint:disable=W0613
    # https://django-simple-history.readthedocs.io/en/latest/user_tracking.html
    """Method for django-simple-history to assign the user who made the change
    to the History history_user field. Deals with the case where
    a User is deleting his or her own profile and setting the history_user
    to the User's or his or her related object's id will result in an
    IntegrityError."""
    # Check if there's a request with an authenticated user
    if request and request.user and request.user.is_authenticated:
        # Check if the request is for deleting a user
        if request.path.endswith(reverse("users:delete")):
            # If the request user is the same as the user being deleted:
            if request.user.id == instance.user.id:
                # Set the history_user to None
                return None
        return request.user
    return None
