from http import HTTPStatus

from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from django_htmx.http import HttpResponseClientRefresh

from gouthelper_ninja.goutdetails.forms import GoutDetailForm
from gouthelper_ninja.goutdetails.views import GoutDetailUpdateView
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory
from gouthelper_ninja.utils.tests.helpers import dummy_get_response


class TestGoutDetailUpdateView(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.patient = PatientFactory()
        self.provider = UserFactory()
        self.goutdetail = self.patient.goutdetail
        self.url = reverse("goutdetails:update", kwargs={"pk": self.goutdetail.id})

        # GET request setup
        self.get_request = self.rf.get(self.url)
        self.get_request.user = self.provider
        self.get_view = GoutDetailUpdateView()
        self.get_view.request = self.get_request
        self.get_view.object = self.goutdetail
        self.get_view.patient = self.patient

        # POST request setup
        self.post_data = {
            "at_goal": True,
            "at_goal_long_term": True,
            "flaring": False,
            "on_ppx": True,
            "on_ult": False,
            "starting_ult": True,
        }
        self.post_request = self.rf.post(self.url, self.post_data)
        self.post_request.user = self.provider
        self.post_request.htmx = False
        self.post_view = GoutDetailUpdateView(kwargs={"pk": self.goutdetail.id})
        self.post_view.request = self.post_request
        self.post_view.object = self.goutdetail
        self.post_view.patient = self.patient

    def test_get_permission_object(self):
        assert self.get_view.get_permission_object() == self.goutdetail

    def test_get_form_kwargs(self):
        form_kwargs = self.get_view.get_form_kwargs()
        assert form_kwargs["initial"] == {
            "at_goal": self.goutdetail.at_goal,
            "at_goal_long_term": self.goutdetail.at_goal_long_term,
            "flaring": self.goutdetail.flaring,
            "on_ppx": self.goutdetail.on_ppx,
            "on_ult": self.goutdetail.on_ult,
            "starting_ult": self.goutdetail.starting_ult,
        }
        assert form_kwargs["patient"] == self.patient
        assert form_kwargs["request_user"] == self.provider
        assert "str_attrs" in form_kwargs
        assert isinstance(form_kwargs["str_attrs"], dict)

    def test_subform_kwargs(self):
        subform_kwargs = self.get_view.subform_kwargs
        assert subform_kwargs["patient"] == self.patient
        assert subform_kwargs["request_user"] == self.provider
        assert "str_attrs" in subform_kwargs
        assert isinstance(subform_kwargs["str_attrs"], dict)

    def test_request_user(self):
        assert self.get_view.request_user == self.provider

    def test_get_context_data(self):
        self.get_view.setup(self.get_request, pk=self.goutdetail.id)
        self.get_view.object = self.get_view.get_object()
        context = self.get_view.get_context_data()
        assert "form" in context
        assert isinstance(context["form"], GoutDetailForm)
        assert context["form"].initial["at_goal"] == self.goutdetail.at_goal
        # goutdetail_form is not set because model is GoutDetail
        assert "goutdetail_form" not in context

    def test_post(self):
        SessionMiddleware(dummy_get_response).process_request(self.post_request)
        MessageMiddleware(dummy_get_response).process_request(self.post_request)
        response = self.post_view.post(self.post_request)
        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == self.patient.get_absolute_url()
        self.goutdetail.refresh_from_db()
        assert self.goutdetail.at_goal is True
        assert self.goutdetail.at_goal_long_term is True
        assert self.goutdetail.flaring is False
        assert self.goutdetail.on_ppx is True
        assert self.goutdetail.on_ult is False
        assert self.goutdetail.starting_ult is True

    def test_post_init(self):
        self.post_view.forms = {}
        assert not hasattr(self.post_view, "form") or not self.post_view.forms.get(
            "form",
        )
        self.post_view.post_init()
        assert hasattr(self.post_view, "forms") is True
        assert isinstance(self.post_view.forms.get("form"), GoutDetailForm)

    def test_post_forms_valid(self):
        self.post_view.forms = {}
        self.post_view.post_init()
        assert not hasattr(self.post_view.forms["form"], "cleaned_data")
        assert self.post_view.post_forms_valid() is True
        assert hasattr(self.post_view.forms["form"], "cleaned_data") is True
        assert self.post_view.forms["form"].cleaned_data["at_goal"] is True

    def test_get_endpoint(self):
        self.client.force_login(self.provider)
        response = self.client.get(self.url)
        assert response.status_code == HTTPStatus.OK

    def test_post_endpoint(self):
        self.client.force_login(self.provider)
        response = self.client.post(self.url, self.post_data)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == self.patient.get_absolute_url()
        self.goutdetail.refresh_from_db()
        assert self.goutdetail.at_goal is True
        assert self.goutdetail.at_goal_long_term is True
        assert self.goutdetail.flaring is False
        assert self.goutdetail.on_ppx is True
        assert self.goutdetail.on_ult is False
        assert self.goutdetail.starting_ult is True

    def test_post_endpoint_errors(self):
        self.client.force_login(self.provider)
        response = self.client.post(self.url, {"at_goal": "INVALID"})
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        assert isinstance(response.context["form"], GoutDetailForm)
        assert not response.context["form"].is_valid()
        assert "at_goal" in response.context["form"].errors

    def test_post_endpoint_htmx(self):
        self.client.force_login(self.provider)
        response = self.client.post(
            self.url,
            self.post_data,
            headers={"hx-request": "true"},
        )
        assert response.status_code == HTTPStatus.OK
        assert isinstance(response, HttpResponseClientRefresh)
        self.goutdetail.refresh_from_db()
        assert self.goutdetail.at_goal is True
