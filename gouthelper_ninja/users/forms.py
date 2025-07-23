from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.utils.translation import gettext_lazy as _

from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.models import User
from gouthelper_ninja.utils.forms import GoutHelperForm


class PatientForm(GoutHelperForm):
    """Form for creating Patient objects."""

    model = Patient

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: Insert demographics Div if required
        # Dateofbirth and gender forms above menopause form
        self.insert_extra_form(
            form_model="dateofbirth",
        )
        self.insert_extra_form(
            form_model="gender",
        )
        self.insert_extra_form(
            form_model="menopause",
        )
        # Insert ethnicity form
        self.insert_extra_form(
            form_model="ethnicity",
        )
        # Insert gout form
        self.insert_extra_form(
            form_model="gout",
        )
        # Insert gout detail form
        self.insert_extra_form(
            form_model="goutdetail",
        )


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):  # type: ignore[name-defined]
        model = User


class UserAdminCreationForm(admin_forms.AdminUserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):  # type: ignore[name-defined]
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
