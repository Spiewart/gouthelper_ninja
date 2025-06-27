"""Module for all Form Tests."""

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from gouthelper_ninja.users.forms import PatientForm
from gouthelper_ninja.users.forms import UserAdminCreationForm
from gouthelper_ninja.users.models import User
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory
from gouthelper_ninja.utils.tests.helpers import create_form_kwargs


class TestPatientForm(TestCase):
    """Test class for all tests related to the PatientForm"""

    def setUp(self):
        self.patient = PatientFactory()
        self.user = UserFactory()
        self.kwargs = create_form_kwargs(
            patient=self.patient,
            request_user=self.user,
        )
        self.form = PatientForm(**self.kwargs)

    def test__gouthelper_form_attrs_set(self):
        """Test that patient, request_user, and str_attrs are set per the parent
        class GoutHelperForm."""

        assert self.form.patient == self.patient
        assert self.form.request_user == self.user
        assert self.form.str_attrs
        assert isinstance(self.form.str_attrs, dict)

    def test__extra_forms_inserted(self):
        """Test that extra forms are inserted correctly. I find this easier
        to do by checking the rendered content of the response."""

        response = self.client.get(reverse("users:patient-create"))

        assert "dateofbirth" in response.rendered_content
        assert "gender" in response.rendered_content
        assert "ethnicity" in response.rendered_content


class TestUserAdminCreationForm:
    """
    Test class for all tests related to the UserAdminCreationForm
    """

    def test_username_validation_error_msg(self, user: User):
        """
        Tests UserAdminCreation Form's unique validator functions correctly by testing:
            1) A new user with an existing username cannot be added.
            2) Only 1 error is raised by the UserCreation Form
            3) The desired error message is raised
        """

        # The user already exists,
        # hence cannot be created.
        form = UserAdminCreationForm(
            {
                "username": user.username,
                "password1": user.password,
                "password2": user.password,
            },
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "username" in form.errors
        assert form.errors["username"][0] == _("This username has already been taken.")
