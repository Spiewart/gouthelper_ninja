from django.urls import reverse


def get_user_change(instance, request, **kwargs):  # pylint:disable=W0613
    # https://django-simple-history.readthedocs.io/en/latest/user_tracking.html
    """Method for django-simple-history to assign the user who made the change
    to the History history_user field. Deals with the case where
    a User is deleting his or her own profile and setting the history_user
    to the User's or his or her related object's id will result in an
    IntegrityError.

    Uses user-specific method (hence not the same as every
    other GoutHelper model, which uses the method in utils/helpers.py)."""
    # Check if there's a request with an authenticated user
    if request and request.user and request.user.is_authenticated:
        # Check if the request is for deleting a user
        if request.path.endswith(reverse("users:delete")):
            # If the request user is the same as the user being deleted:
            if request.user.id == instance.id:
                # Set the history_user to None
                return None
        return request.user
    return None
