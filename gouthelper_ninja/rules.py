"""Gouthelper-wide rules for object-level permissions. If an
app has unique permissions, such as the users app, it should
define its own rules in its own rules.py file.
"""

from typing import TYPE_CHECKING
from uuid import UUID

import rules
from django.contrib.auth.models import AnonymousUser

from gouthelper_ninja.users.choices import Roles

if TYPE_CHECKING:
    from django.db.models import Model

    from gouthelper_ninja.users.models import Patient
    from gouthelper_ninja.users.models import User


@rules.predicate
def obj_not_none(_, obj: "Model") -> bool:
    """Returns True if the object is not None."""
    return obj is not None


@rules.predicate
def obj_patient_without_provider(_, obj: "Model"):
    """Returns True if the object's Patient does not have a provider."""
    return obj.patient.patientprofile.provider is None


@rules.predicate
def obj_patient_without_creator(_, obj: "Model"):
    """Returns True if the object's Patient does not have a creator."""
    return obj.patient.creator is None


@rules.predicate
def obj_without_creator(_, obj: "Model"):
    """Returns True if the object does not have a creator."""
    return obj.creator is None


@rules.predicate
def obj_without_provider(_, obj: "Model"):
    """Returns True if the object does not have a provider."""
    return obj.patientprofile.provider is None


@rules.predicate
def user_is_admin(user: "User") -> bool:
    """Returns True if the user is an admin."""

    return user.role == Roles.ADMIN


@rules.predicate
def user_is_anonymous(user: "User") -> bool:
    """Returns True if the user is an AnonymousUser."""

    return isinstance(user, AnonymousUser)


@rules.predicate
def user_is_obj_patient(user: "User", obj: "Model"):
    return obj.patient == user


@rules.predicate
def user_is_obj_patients_provider(user: "User", obj: "Model"):
    return obj.patient.patientprofile.provider == user


@rules.predicate
def user_is_obj_patients_creator(user: "User", obj: "Model"):
    return obj.patient.creator == user


@rules.predicate
def user_id_is_obj(user: "User", obj: str | UUID | None):
    """Returns True if the user's id matches the obj,
    which should be a provider_id kwarg."""

    return (
        (user.id == obj if isinstance(obj, UUID) else str(user.id) == obj)
        if obj
        else False
    )


@rules.predicate
def user_is_obj(user: "User", obj: "User") -> bool:
    """Returns True if the user is the same as the object."""

    return user.id == obj.id


@rules.predicate
def user_is_obj_creator(user: "User", obj: "User") -> bool:
    """Returns True if the creator of the object (Patient) is the user.
    Need to ensure that the object is a Patient first."""

    creator = getattr(obj, "creator", None)
    return creator is not None and creator.id == user.id


@rules.predicate
def user_is_obj_provider(user: "User", obj: "Patient") -> bool:
    """Returns True if the user is the provider of the patient.
    Need to ensure that the object is a Patient first."""

    provider = getattr(obj.patientprofile, "provider", None)
    return provider is not None and provider.id == user.id


add_object = ~user_is_anonymous & (
    user_is_admin
    | (obj_not_none & (user_is_obj | user_is_obj_provider | user_is_obj_creator))
) | (obj_without_provider & obj_without_creator)
delete_object = ~user_is_anonymous & (
    user_is_admin
    | user_is_obj_patient
    | user_is_obj_patients_provider
    | user_is_obj_patients_creator
)
change_object = delete_object | (
    obj_patient_without_provider & obj_patient_without_creator
)
view_object = change_object


rules.add_rule("can_add_object", add_object)
rules.add_rule("can_change_object", change_object)
rules.add_rule("can_delete_object", delete_object)
rules.add_rule("can_view_object", view_object)
