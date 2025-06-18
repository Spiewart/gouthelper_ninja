from typing import TYPE_CHECKING

import rules

from gouthelper_ninja.rules import user_id_is_obj
from gouthelper_ninja.rules import user_is_admin
from gouthelper_ninja.rules import user_is_anonymous
from gouthelper_ninja.rules import user_is_obj
from gouthelper_ninja.rules import user_is_obj_creator
from gouthelper_ninja.rules import user_is_obj_provider
from gouthelper_ninja.users.choices import Roles

if TYPE_CHECKING:
    from gouthelper_ninja.users.models import User


@rules.predicate
def obj_without_provider(_, obj: "User") -> bool:
    """Returns True if the object (Patient) does not have a provider.
    Need to ensure that the object is a Patient first."""

    return obj.patientprofile.provider is None


@rules.predicate
def obj_without_creator(_, obj: "User") -> bool:
    """Returns True if the object (Patient) does not have a creator.
    Need to ensure that the object is a Patient first."""

    return getattr(obj, "creator", None) is None


@rules.predicate
def obj_is_pseudopatient(user: "User") -> bool:
    """Returns True if the object is a Pseudopatient."""

    return user_is_anonymous(user) or user.role == Roles.PSEUDOPATIENT


@rules.predicate
def obj_is_patient_or_pseudopatient(_, obj: "User") -> bool:
    """Returns True if the object is a Patient or Pseudopatient.
    Need to ensure that the object is a Patient first."""

    return obj.role in {Roles.PATIENT, Roles.PSEUDOPATIENT}


@rules.predicate
def user_is_patient(user: "User") -> bool:
    """Returns True if the object is a Patient."""

    return user.role == Roles.PATIENT


@rules.predicate
def user_is_a_provider(user: "User") -> bool:
    """Returns True if the user is a Provider."""

    return user.role == Roles.PROVIDER


@rules.predicate
def user_username_is_obj(user: "User", obj: str | None):
    """Returns True if the user's username matches the obj,
    which should be a provider kwarg."""

    return user.username == obj if obj else False


# Patient predicates
add_provider_patient = ~user_is_anonymous & (
    # Important: requires checking if the User indicated by the
    # obj (either username or id) exists in the view or API.
    user_is_admin | (user_is_a_provider & (user_username_is_obj | user_id_is_obj))
)

change_patient = (
    ~user_is_anonymous
    & obj_is_patient_or_pseudopatient
    & (
        user_is_admin
        | user_is_obj
        | user_is_obj_provider
        | (obj_without_provider & (obj_without_creator | user_is_obj_creator))
    )
) | (
    user_is_anonymous
    & obj_is_patient_or_pseudopatient
    & obj_without_provider
    & obj_without_creator
)

delete_patient = (
    ~user_is_anonymous
    & obj_is_patient_or_pseudopatient
    & (user_is_admin | user_is_obj | user_is_obj_provider | user_is_obj_creator)
)

view_patient = change_patient

# Provider predicates
# Permissions to view the provider list are the same as to add a Patient
# for a specific provider.
view_provider_list = add_provider_patient

# User predicates
change_user = ~user_is_anonymous & (user_is_obj | user_is_admin)
delete_user = change_user
view_user = change_user

# Patient rules and permissions
rules.add_rule("can_add_provider_patient", add_provider_patient)
rules.add_perm("users.can_add_provider_patient", add_provider_patient)
rules.add_rule("can_delete_patient", delete_patient)
rules.add_perm("users.can_delete_patient", delete_patient)
rules.add_rule("can_edit_patient", change_patient)
rules.add_perm("users.can_edit_patient", change_patient)
rules.add_rule("can_view_patient", view_patient)
rules.add_perm("users.can_view_patient", view_patient)

# Provider rules and permissions
rules.add_rule("can_view_provider_list", view_provider_list)
rules.add_perm("users.can_view_provider_list", view_provider_list)

# User rules and permissions
rules.add_rule("can_delete_user", delete_user)
rules.add_perm("users.can_delete_user", delete_user)
rules.add_rule("can_edit_user", change_user)
rules.add_perm("users.can_edit_user", change_user)
rules.add_rule("can_view_user", view_user)
rules.add_perm("users.can_view_user", view_user)
