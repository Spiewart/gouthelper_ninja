from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from gouthelper_ninja.dateofbirths.forms import DateOfBirthForm
from gouthelper_ninja.dateofbirths.views import DateOfBirthUpdateView
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory
from gouthelper_ninja.utils.helpers import age_calc
from gouthelper_ninja.utils.test_helpers import RESPONSE_REDIRECT_STATUS
from gouthelper_ninja.utils.test_helpers import dummy_get_response


class TestDateOfBirthUpdateView(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.patient = PatientFactory()
        self.provider = UserFactory()
        self.dob = self.patient.dateofbirth
        self.new_age = age_calc(self.dob.dateofbirth) + 10
        self.get = self.rf.get(
            reverse("dateofbirths:update", kwargs={"pk": self.dob.id}),
        )
        self.get.user = self.provider
        self.get_view = DateOfBirthUpdateView()
        self.get_view.request = self.get
        self.post = self.rf.post(
            reverse("dateofbirths:update", kwargs={"pk": self.dob.id}),
            {"dateofbirth": self.new_age},
        )
        self.post.user = self.provider
        # Set HTMX to False to avoid HTMX-specific behavior in the test
        self.post.htmx = False
        self.post_view = DateOfBirthUpdateView()
        self.post_view.request = self.post

    def test__get_permission_object(self):
        self.get_view.object = self.dob

        assert self.get_view.get_permission_object() == self.patient

    def test__get_form_kwargs(self):
        self.get_view.object = self.dob

        form_kwargs = self.get_view.get_form_kwargs()
        assert form_kwargs["initial"] == {"dateofbirth": self.dob.dateofbirth}
        assert form_kwargs["patient"] == self.patient
        assert form_kwargs["request_user"] == self.provider
        assert "str_attrs" in form_kwargs
        assert isinstance(form_kwargs["str_attrs"], dict)

    def test__subform_kwargs(self):
        self.get_view.object = self.dob

        subform_kwargs = self.get_view.subform_kwargs
        assert subform_kwargs["patient"] == self.patient
        assert subform_kwargs["request_user"] == self.provider
        assert "str_attrs" in subform_kwargs
        assert isinstance(subform_kwargs["str_attrs"], dict)

    def test__request_user(self):
        assert self.get_view.request_user == self.provider

    def test__get_context_data(self):
        self.get_view.object = self.dob

        context = self.get_view.get_context_data()

        assert "dateofbirth_form" not in context
        assert "form" in context
        assert isinstance(context["form"], DateOfBirthForm)
        assert context["form"].initial == {"dateofbirth": self.dob.dateofbirth}

    def test__post(self):
        self.post_view.object = self.dob

        SessionMiddleware(dummy_get_response).process_request(self.post)
        MessageMiddleware(dummy_get_response).process_request(self.post)

        response = self.post_view.post(self.post)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == RESPONSE_REDIRECT_STATUS
        assert response.url == reverse(
            "users:detail",
            kwargs={"username": self.patient.username},
        )
        self.dob.refresh_from_db()
        assert age_calc(self.dob.dateofbirth) == self.new_age

    def test__post_init(self):
        self.post_view.object = self.dob

        assert hasattr(self.post_view, "form") is False

        self.post_view.post_init(self.post)

        assert hasattr(self.post_view, "form") is True
        assert isinstance(self.post_view.form, DateOfBirthForm)

    def test__post_forms_valid(self):
        self.post_view.object = self.dob
        self.post_view.post_init(self.post)

        assert hasattr(self.post_view.form, "cleaned_data") is False

        assert self.post_view.post_forms_valid() is True

        assert hasattr(self.post_view.form, "cleaned_data") is True

        assert self.post_view.form.cleaned_data == {"dateofbirth": self.new_age}
