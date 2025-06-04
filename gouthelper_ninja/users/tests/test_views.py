from http import HTTPStatus

import pytest
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from gouthelper_ninja.dateofbirths.forms import DateOfBirthForm
from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.ethnicitys.forms import EthnicityForm
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.forms import GenderForm
from gouthelper_ninja.users.forms import UserAdminChangeForm
from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.models import User
from gouthelper_ninja.users.tests.factories import UserFactory
from gouthelper_ninja.users.views import PatientCreateView
from gouthelper_ninja.users.views import UserRedirectView
from gouthelper_ninja.users.views import UserUpdateView
from gouthelper_ninja.users.views import user_detail_view
from gouthelper_ninja.utils.helpers import get_str_attrs_dict
from gouthelper_ninja.utils.test_helpers import dummy_get_response

pytestmark = pytest.mark.django_db


RESPONSE_STATUS = 200
RESPONSE_REDIRECT_STATUS = 302


class TestPatientCreateView(TestCase):
    def setUp(self):
        self.provider = UserFactory()
        self.rf = RequestFactory()
        self.data = {
            "dateofbirth": 70,
            "ethnicity": Ethnicitys.CAUCASIAN,
            "gender": Genders.FEMALE,
        }

        self.get = self.rf.get(
            reverse("users:patient-create"),
        )
        self.get.user = self.provider
        self.get_view = PatientCreateView()
        self.get_view.setup(self.get)
        self.get_view.object = None

        self.post = self.rf.post(
            reverse("users:patient-create"),
            data=self.data,
        )
        self.post.user = self.provider
        self.post_view = PatientCreateView(kwargs={})

        self.post_view.request = self.post
        self.post_view.request.htmx = (
            False  # Set HTMX to False to avoid HTMX-specific behavior in the test
        )
        self.post_view.object = None

        self.get_provider = self.rf.get(
            reverse(
                "users:provider-patient-create",
                kwargs={"provider": self.provider.username},
            ),
        )

        self.get_provider.user = self.provider
        self.get_provider_view = PatientCreateView(
            kwargs={"provider": self.provider.username},
        )
        self.get_provider_view.request = self.get_provider
        self.get_provider_view.object = None

        self.post_provider = self.rf.post(
            reverse(
                "users:provider-patient-create",
                kwargs={"provider": self.provider.username},
            ),
            data=self.data,
        )
        self.post_provider.user = self.provider
        self.post_provider_view = PatientCreateView(
            kwargs={"provider": self.provider.username},
        )
        self.post_provider_view.request = self.post_provider
        self.post_provider_view.request.htmx = (
            False  # Set HTMX to False to avoid HTMX-specific behavior in the test
        )
        self.post_provider_view.object = None

    def test__get_permission_object(self):
        assert self.get_view.get_permission_object() is None
        assert self.get_provider_view.get_permission_object() == self.provider

    def test__get_form_kwargs(self):
        form_kwargs = self.get_view.get_form_kwargs()
        assert "initial" in form_kwargs
        assert not form_kwargs["initial"]
        assert form_kwargs["patient"] is None
        assert form_kwargs["request_user"] == self.provider
        assert "str_attrs" in form_kwargs
        assert isinstance(form_kwargs["str_attrs"], dict)

    def test__get_initial(self):
        initial = self.get_view.get_initial()
        assert initial == {}

    def test__subform_kwargs(self):
        subform_kwargs = self.get_view.subform_kwargs
        assert subform_kwargs["patient"] is None
        assert subform_kwargs["request_user"] == self.provider
        assert "str_attrs" in subform_kwargs
        assert isinstance(subform_kwargs["str_attrs"], dict)

    def test__request_user(self):
        assert self.get_view.request_user == self.provider

    def test__get_context_data(self):
        context = self.get_view.get_context_data()

        assert "form" in context
        assert isinstance(context["form"], PatientCreateView.form_class)
        assert context["form"].initial == {}
        assert "patient_form" not in context
        assert "dateofbirth_form" in context
        assert isinstance(context["dateofbirth_form"], DateOfBirthForm)
        assert "ethnicity_form" in context
        assert isinstance(context["ethnicity_form"], EthnicityForm)
        assert "gender_form" in context
        assert isinstance(context["gender_form"], GenderForm)

    def test__patient(self):
        assert self.get_view.patient is None

    def test__provider(self):
        assert self.get_view.provider is None
        assert self.get_provider_view.provider == self.provider

    def test__str_attrs(self):
        assert self.get_view.str_attrs
        assert isinstance(self.get_view.str_attrs, dict)
        assert self.get_view.str_attrs == get_str_attrs_dict(
            None,
            self.get_view.request_user,
        )

    def test__post(self):
        num_patients = Patient.objects.count()
        assert num_patients == 0

        SessionMiddleware(dummy_get_response).process_request(self.post)
        MessageMiddleware(dummy_get_response).process_request(self.post)

        response = self.post_view.post(self.post)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == RESPONSE_REDIRECT_STATUS

        patient = Patient.objects.order_by("created").last()
        assert response.url == reverse(
            "users:detail",
            kwargs={"username": patient.username},
        )

        assert Patient.objects.count() == num_patients + 1

    def test__post_with_errors(self):
        # Test with invalid data
        invalid_data = self.data.copy()
        invalid_data["dateofbirth"] = "invalid_date"

        self.post_view.request.POST = invalid_data

        SessionMiddleware(dummy_get_response).process_request(self.post)
        MessageMiddleware(dummy_get_response).process_request(self.post)

        response = self.post_view.post(self.post)

        assert response.status_code == RESPONSE_STATUS
        assert isinstance(response, HttpResponseRedirect) is False
        assert isinstance(response, HttpResponse)
        assert "form" in response.context_data
        assert not response.context_data["form"].errors
        assert "dateofbirth_form" in response.context_data
        assert response.context_data["dateofbirth_form"].errors
        assert "ethnicity_form" in response.context_data
        assert not response.context_data["ethnicity_form"].errors
        assert "gender_form" in response.context_data
        assert not response.context_data["gender_form"].errors

    def test__post_with_provider(self):
        num_patients = Patient.objects.count()
        assert num_patients == 0

        SessionMiddleware(dummy_get_response).process_request(self.post_provider)
        MessageMiddleware(dummy_get_response).process_request(self.post_provider)

        response = self.post_provider_view.post(self.post_provider)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == RESPONSE_REDIRECT_STATUS

        patient = Patient.objects.order_by("created").last()
        assert response.url == reverse(
            "users:detail",
            kwargs={"username": patient.username},
        )

        assert Patient.objects.count() == num_patients + 1
        assert patient.provider == self.provider


class TestUserUpdateView:
    """
    TODO:
        extracting view initialization code as class-scoped fixture
        would be great if only pytest-django supported non-function-scoped
        fixture db access -- this is a work-in-progress for now:
        https://github.com/pytest-dev/pytest-django/pull/258
    """

    def dummy_get_response(self, request: HttpRequest):
        return None

    def test_get_success_url(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request
        assert view.get_success_url() == f"/users/{user.username}/"

    def test_get_object(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_object() == user

    def test_form_valid(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")

        # Add the session/message middleware to the request
        SessionMiddleware(self.dummy_get_response).process_request(request)
        MessageMiddleware(self.dummy_get_response).process_request(request)
        request.user = user

        view.request = request

        # Initialize the form
        form = UserAdminChangeForm()
        form.cleaned_data = {}
        form.instance = user
        view.form_valid(form)

        messages_sent = [m.message for m in messages.get_messages(request)]
        assert messages_sent == [_("Information successfully updated")]


class TestUserRedirectView:
    def test_get_redirect_url(self, user: User, rf: RequestFactory):
        view = UserRedirectView()
        request = rf.get("/fake-url")
        request.user = user

        view.request = request
        assert view.get_redirect_url() == f"/users/{user.username}/"


class TestUserDetailView:
    def test_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = UserFactory()
        response = user_detail_view(request, username=user.username)

        assert response.status_code == HTTPStatus.OK

    def test_not_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = AnonymousUser()
        response = user_detail_view(request, username=user.username)
        login_url = reverse(settings.LOGIN_URL)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == f"{login_url}?next=/fake-url/"
