from http import HTTPStatus

from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from django_htmx.http import HttpResponseClientRefresh

from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.forms import GenderForm
from gouthelper_ninja.genders.views import GenderEditMixin
from gouthelper_ninja.genders.views import GenderUpdateView
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory
from gouthelper_ninja.utils.tests.helpers import dummy_get_response


class TestGenderUpdateView(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        # Assuming PatientFactory creates an associated Gender object
        self.patient = PatientFactory()
        self.provider = UserFactory()
        self.gender_obj = self.patient.gender
        self.original_gender_value = self.gender_obj.gender  # This is an int

        # Determine a new gender value different from the original
        if self.original_gender_value == Genders.MALE.value:
            self.new_gender_value = Genders.FEMALE.value
        else:
            self.new_gender_value = Genders.MALE.value

        self.url = reverse("genders:update", kwargs={"pk": self.gender_obj.id})

        # GET request setup
        self.get_request = self.rf.get(self.url)
        self.get_request.user = self.provider
        self.get_view = GenderUpdateView()
        self.get_view.request = self.get_request
        self.get_view.object = self.gender_obj
        # Manually set patient for mixin properties that might need it before dispatch
        self.get_view.patient = self.patient

        # POST request setup
        # Form fields submit string values
        self.post_data = {"gender": str(self.new_gender_value)}
        self.post_request = self.rf.post(self.url, self.post_data)
        self.post_request.user = self.provider
        self.post_request.htmx = False  # Default to non-HTMX for most tests
        self.post_view = GenderUpdateView(kwargs={"pk": self.gender_obj.id})
        self.post_view.request = self.post_request
        self.post_view.object = self.gender_obj
        # Manually set patient for mixin properties
        self.post_view.patient = self.patient

    def test__get_permission_object(self):
        assert self.get_view.get_permission_object() == self.gender_obj

    def test__get_form_kwargs(self):
        form_kwargs = self.get_view.get_form_kwargs()
        assert form_kwargs["initial"] == {"gender": self.original_gender_value}
        assert form_kwargs["patient"] == self.patient
        assert form_kwargs["request_user"] == self.provider
        assert "str_attrs" in form_kwargs
        assert isinstance(form_kwargs["str_attrs"], dict)

    def test__subform_kwargs(self):
        subform_kwargs = self.get_view.subform_kwargs
        assert subform_kwargs["patient"] == self.patient
        assert subform_kwargs["request_user"] == self.provider
        assert "str_attrs" in subform_kwargs
        assert isinstance(subform_kwargs["str_attrs"], dict)

    def test__request_user(self):
        assert self.get_view.request_user == self.provider

    def test__get_context_data(self):
        # Need to run setup_view if object is not set by dispatch
        self.get_view.setup(self.get_request, pk=self.gender_obj.id)
        self.get_view.object = self.get_view.get_object()  # Ensure object is loaded
        context = self.get_view.get_context_data()

        # For GenderUpdateView, self.model IS Gender,
        # so gender_form is not set by GenderEditMixin
        assert "gender_form" not in context
        assert "form" in context
        assert isinstance(context["form"], GenderForm)
        assert context["form"].initial == {"gender": self.original_gender_value}

    def test__post(self):
        SessionMiddleware(dummy_get_response).process_request(self.post_request)
        MessageMiddleware(dummy_get_response).process_request(self.post_request)

        response = self.post_view.post(self.post_request)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == reverse(
            "users:patient-detail",
            kwargs={"patient": self.patient.id},
        )
        self.gender_obj.refresh_from_db()
        assert self.gender_obj.gender == self.new_gender_value

    def test__post_init(self):
        self.post_view.forms = {}  # Reset forms
        assert not hasattr(self.post_view, "form") or not self.post_view.forms.get(
            "form",
        )
        # For GenderUpdateView, self.model IS Gender, so GenderEditMixin's
        # specific block is skipped.
        # GoutHelperEditMixin.post_init will set up self.forms["form"]
        self.post_view.post_init()
        assert hasattr(self.post_view, "forms") is True
        assert isinstance(self.post_view.forms.get("form"), GenderForm)

    def test__post_forms_valid(self):
        self.post_view.forms = {}  # Reset forms
        self.post_view.post_init()
        assert not hasattr(self.post_view.forms["form"], "cleaned_data")
        assert self.post_view.post_forms_valid() is True
        assert hasattr(self.post_view.forms["form"], "cleaned_data") is True
        # GenderForm.clean_gender converts to enum
        expected_cleaned_gender = Genders(self.new_gender_value)
        assert self.post_view.forms["form"].cleaned_data == {
            "gender": expected_cleaned_gender,
        }

    def test__get_endpoint(self):
        self.client.force_login(self.provider)
        response = self.client.get(self.url)
        assert response.status_code == HTTPStatus.OK

    def test__post_endpoint(self):
        self.client.force_login(self.provider)
        response = self.client.post(self.url, self.post_data)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == reverse(
            "users:patient-detail",
            kwargs={"patient": self.patient.id},
        )
        self.gender_obj.refresh_from_db()
        assert self.gender_obj.gender == self.new_gender_value

    def test__post_endpoint_errors(self):
        self.client.force_login(self.provider)
        response = self.client.post(self.url, {"gender": "INVALID_GENDER_VALUE"})
        assert response.status_code == HTTPStatus.OK  # Form redisplay
        assert "form" in response.context
        assert isinstance(response.context["form"], GenderForm)
        assert not response.context["form"].is_valid()
        assert "gender" in response.context["form"].errors

    def test__post_endpoint_htmx(self):
        self.client.force_login(self.provider)
        response = self.client.post(
            self.url,
            self.post_data,
            headers={"hx-request": "true"},
        )
        assert response.status_code == HTTPStatus.OK
        assert isinstance(response, HttpResponseClientRefresh)
        self.gender_obj.refresh_from_db()
        assert self.gender_obj.gender == self.new_gender_value


class TestGenderEditMixin(TestCase):
    def test_get_gender_initial_with_patient(self):
        class DummyGender:
            gender = Genders.FEMALE

        class DummyPatient:
            gender = DummyGender()

        mixin = GenderEditMixin()
        mixin.patient = DummyPatient()
        result = mixin.get_gender_initial()
        assert result == {"gender": Genders.FEMALE}

    def test_get_gender_initial_without_patient(self):
        mixin = GenderEditMixin()
        mixin.patient = None
        result = mixin.get_gender_initial()
        assert result == {}

    def test_get_gender_initial_patient_no_gender(self):
        class NoGenderPatient:
            pass

        mixin = GenderEditMixin()
        mixin.patient = NoGenderPatient()
        result = mixin.get_gender_initial()
        assert result == {}
        assert result == {}
