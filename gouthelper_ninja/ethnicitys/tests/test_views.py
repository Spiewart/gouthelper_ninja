from http import HTTPStatus

from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from django_htmx.http import HttpResponseClientRefresh

from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.ethnicitys.forms import EthnicityForm
from gouthelper_ninja.ethnicitys.views import EthnicityEditMixin
from gouthelper_ninja.ethnicitys.views import EthnicityUpdateView
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory
from gouthelper_ninja.utils.tests.helpers import dummy_get_response


class TestEthnicityUpdateView(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.patient = PatientFactory()  # This should create an associated Ethnicity
        self.provider = UserFactory()
        self.ethnicity_obj = self.patient.ethnicity
        self.original_ethnicity_value = self.ethnicity_obj.ethnicity

        # Determine a new ethnicity value different from the original
        if self.original_ethnicity_value == Ethnicitys.AFRICANAMERICAN.value:
            self.new_ethnicity_value = Ethnicitys.CAUCASIAN.value
        else:
            self.new_ethnicity_value = Ethnicitys.AFRICANAMERICAN.value

        self.url = reverse("ethnicitys:update", kwargs={"pk": self.ethnicity_obj.id})

        # GET request setup
        self.get_request = self.rf.get(self.url)
        self.get_request.user = self.provider
        self.get_view = EthnicityUpdateView()
        self.get_view.request = self.get_request
        self.get_view.object = self.ethnicity_obj
        # Manually set patient for mixin properties that might need it before dispatch
        self.get_view.patient = self.patient

        # POST request setup
        self.post_data = {"ethnicity": self.new_ethnicity_value}
        self.post_request = self.rf.post(self.url, self.post_data)
        self.post_request.user = self.provider
        self.post_request.htmx = False  # Default to non-HTMX for most tests
        self.post_view = EthnicityUpdateView(kwargs={"pk": self.ethnicity_obj.id})
        self.post_view.request = self.post_request
        self.post_view.object = self.ethnicity_obj
        # Manually set patient for mixin properties
        self.post_view.patient = self.patient

    def test__get_permission_object(self):
        assert self.get_view.get_permission_object() == self.ethnicity_obj

    def test__get_form_kwargs(self):
        form_kwargs = self.get_view.get_form_kwargs()
        assert form_kwargs["initial"] == {"ethnicity": self.original_ethnicity_value}
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
        self.get_view.setup(self.get_request, pk=self.ethnicity_obj.id)
        self.get_view.object = self.get_view.get_object()  # Ensure object is loaded
        context = self.get_view.get_context_data()

        assert "ethnicity_form" not in context  # Main form is 'form'
        assert "form" in context
        assert isinstance(context["form"], EthnicityForm)
        assert context["form"].initial == {"ethnicity": self.original_ethnicity_value}

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
        self.ethnicity_obj.refresh_from_db()
        assert self.ethnicity_obj.ethnicity == self.new_ethnicity_value

    def test__post_init(self):
        self.post_view.forms = {}  # Reset forms
        assert not hasattr(self.post_view, "form") or not self.post_view.forms.get(
            "form",
        )
        self.post_view.post_init()
        assert hasattr(self.post_view, "forms") is True
        assert isinstance(self.post_view.forms.get("form"), EthnicityForm)

    def test__post_forms_valid(self):
        self.post_view.forms = {}  # Reset forms
        self.post_view.post_init()
        assert not hasattr(self.post_view.forms["form"], "cleaned_data")
        assert self.post_view.post_forms_valid() is True
        assert hasattr(self.post_view.forms["form"], "cleaned_data") is True
        assert self.post_view.forms["form"].cleaned_data == {
            "ethnicity": self.new_ethnicity_value,
        }

    def test__get_endpoint(self):
        response = self.client.get(self.url)
        assert response.status_code == HTTPStatus.OK

    def test__post_endpoint(self):
        response = self.client.post(self.url, self.post_data)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == reverse(
            "users:patient-detail",
            kwargs={"patient": self.patient.id},
        )
        self.ethnicity_obj.refresh_from_db()
        assert self.ethnicity_obj.ethnicity == self.new_ethnicity_value

    def test__post_endpoint_errors(self):
        response = self.client.post(self.url, {"ethnicity": "INVALID_ETHNICITY"})
        assert response.status_code == HTTPStatus.OK  # Form redisplay
        assert "form" in response.context
        assert isinstance(response.context["form"], EthnicityForm)
        assert not response.context["form"].is_valid()
        assert "ethnicity" in response.context["form"].errors

    def test__post_endpoint_htmx(self):
        """Test that the view returns a django-htmx HttpResponseClientRefresh
        when the request is an HTMX request."""
        response = self.client.post(
            self.url,
            self.post_data,
            headers={"hx-request": "true"},
        )
        assert response.status_code == HTTPStatus.OK
        assert isinstance(response, HttpResponseClientRefresh)
        self.ethnicity_obj.refresh_from_db()
        assert self.ethnicity_obj.ethnicity == self.new_ethnicity_value


class TestEthnicityEditMixin(TestCase):
    def test_get_ethnicity_initial_with_patient(self):
        class DummyEthnicity:
            ethnicity = Ethnicitys.AFRICANAMERICAN

        class DummyPatient:
            ethnicity = DummyEthnicity()

        mixin = EthnicityEditMixin()
        mixin.patient = DummyPatient()
        result = mixin.get_ethnicity_initial()

        assert result == {"ethnicity": Ethnicitys.AFRICANAMERICAN}

    def test_get_ethnicity_initial_without_patient(self):
        mixin = EthnicityEditMixin()
        mixin.patient = None
        result = mixin.get_ethnicity_initial()

        assert result == {}

    def test_get_ethnicity_initial_patient_no_ethnicity(self):
        class NoEthnicityPatient:
            pass

        mixin = EthnicityEditMixin()
        mixin.patient = NoEthnicityPatient()
        result = mixin.get_ethnicity_initial()

        assert result == {}
