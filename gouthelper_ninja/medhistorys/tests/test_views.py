from http import HTTPStatus

import pytest
from django.http import Http404
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from django_htmx.http import HttpResponseClientRefresh

from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.medhistorys.forms import MedHistoryForm
from gouthelper_ninja.medhistorys.models import MedHistory
from gouthelper_ninja.medhistorys.tests.factories import MedHistoryFactory
from gouthelper_ninja.medhistorys.views import MedHistoryCreateView
from gouthelper_ninja.medhistorys.views import MedHistoryMixin
from gouthelper_ninja.medhistorys.views import MedHistoryUpdateView
from gouthelper_ninja.users.tests.factories import PatientFactory


class TestMedHistoryCreateView(TestCase):
    def setUp(self):
        self.patient = PatientFactory()

    def test__get(self):
        url = reverse(
            "medhistorys:create",
            kwargs={
                "patient": self.patient.id,
                "mhtype": MHTypes.DIABETES,
            },
        )
        response = self.client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert response.context["form"]
        assert isinstance(response.context["form"], MedHistoryForm)
        self.assertTemplateUsed(response, "medhistorys/medhistory_form.html")

    def test__post(self):
        assert not self.patient.diabetes

        url = reverse(
            "medhistorys:create",
            kwargs={
                "patient": self.patient.id,
                "mhtype": MHTypes.DIABETES,
            },
        )
        data = {
            "history_of": True,
        }
        response = self.client.post(url, data)
        assert response.status_code == HTTPStatus.FOUND

        # Delete the diabetes cached_property
        delattr(self.patient, "diabetes")

        assert self.patient.diabetes
        assert self.patient.diabetes.history_of is True

    def test__post_htmx(self):
        assert not self.patient.diabetes

        url = reverse(
            "medhistorys:create",
            kwargs={
                "patient": self.patient.id,
                "mhtype": MHTypes.DIABETES,
            },
        )
        data = {
            "history_of": True,
        }
        response = self.client.post(url, data, headers={"hx-request": "true"})
        assert isinstance(response, HttpResponseClientRefresh)
        assert response.status_code == HTTPStatus.OK

        # Delete the diabetes cached_property
        delattr(self.patient, "diabetes")

        assert self.patient.diabetes
        assert self.patient.diabetes.history_of is True

    def test__post_invalid(self):
        url = reverse(
            "medhistorys:create",
            kwargs={
                "patient": self.patient.id,
                "mhtype": MHTypes.DIABETES,
            },
        )
        data = {
            "history_of": "",  # Invalid data
        }
        response = self.client.post(url, data)
        assert response.status_code == HTTPStatus.OK
        assert response.context["form"].errors
        assert isinstance(response.context["form"], MedHistoryForm)
        self.assertTemplateUsed(response, "medhistorys/medhistory_form.html")

    def test__mhtype(self):
        view = MedHistoryCreateView()
        view.kwargs = {
            "patient": self.patient.id,
            "mhtype": MHTypes.DIABETES,
        }
        assert view.mhtype == MHTypes.DIABETES

    def test__mhtype_invalid(self):
        view = MedHistoryCreateView()
        view.kwargs = {
            "patient": self.patient.id,
            "mhtype": "INVALID",
        }
        with pytest.raises(Http404):
            _ = view.mhtype

    def test__dispatch_redirects(self):
        mh = MedHistoryFactory(
            patient=self.patient,
            mhtype=MHTypes.DIABETES,
        )
        url = reverse(
            "medhistorys:create",
            kwargs={
                "patient": self.patient.id,
                "mhtype": MHTypes.DIABETES,
            },
        )
        response = self.client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == reverse(
            "medhistorys:update",
            kwargs={
                "pk": mh.id,
            },
        )


class TestMedHistoryUpdateView(TestCase):
    def setUp(self):
        self.patient = PatientFactory()
        self.mh = MedHistoryFactory(
            patient=self.patient,
            mhtype=MHTypes.DIABETES,
            history_of=True,
        )

    def test__get(self):
        self.client.force_login(self.patient)
        url = reverse(
            "medhistorys:update",
            kwargs={
                "pk": self.mh.id,
            },
        )
        response = self.client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert response.context["form"]
        assert isinstance(response.context["form"], MedHistoryForm)
        self.assertTemplateUsed(response, "medhistorys/medhistory_form.html")

    def test__post(self):
        assert self.patient.diabetes
        assert self.patient.diabetes.history_of is True

        url = reverse(
            "medhistorys:update",
            kwargs={
                "pk": self.mh.id,
            },
        )
        data = {
            "history_of": False,
        }

        response = self.client.post(url, data)
        assert response.status_code == HTTPStatus.FOUND

        # Delete the diabetes cached_property
        delattr(self.patient, "diabetes")

        assert not self.patient.diabetes.history_of

    def test__post_htmx(self):
        assert self.patient.diabetes
        assert self.patient.diabetes.history_of is True

        url = reverse(
            "medhistorys:update",
            kwargs={
                "pk": self.mh.id,
            },
        )
        data = {
            "history_of": False,
        }
        response = self.client.post(url, data, headers={"hx-request": "true"})
        assert isinstance(response, HttpResponseClientRefresh)
        assert response.status_code == HTTPStatus.OK

        # Delete the diabetes cached_property
        delattr(self.patient, "diabetes")

        assert not self.patient.diabetes.history_of

    def test__post_invalid(self):
        url = reverse(
            "medhistorys:update",
            kwargs={
                "pk": self.mh.id,
            },
        )
        data = {
            "history_of": "",  # Invalid data
        }
        response = self.client.post(url, data)
        assert response.status_code == HTTPStatus.OK
        assert response.context["form"].errors
        assert isinstance(response.context["form"], MedHistoryForm)
        self.assertTemplateUsed(response, "medhistorys/medhistory_form.html")

    def test__mhtype(self):
        view = MedHistoryUpdateView()
        view.object = self.mh
        assert view.mhtype == MHTypes.DIABETES

    def test__model(self):
        view = MedHistoryUpdateView()
        assert view.model is MedHistory
        view.object = self.mh
        assert view.model is self.mh.__class__


class TestMedHistoryMixin(TestCase):
    class DummySuper:
        def get_context_data(self, **kwargs):
            return {"foo": "bar"}

        def get_form_kwargs(self):
            return {"baz": 1}

        def get_initial(self):
            return {}

        def get_prefix(self):
            return "dummy"

    class DummyMixin(MedHistoryMixin, DummySuper):
        mhtype = MHTypes.DIABETES
        object = None

    def setUp(self):
        self.mixin = self.DummyMixin()
        rf = RequestFactory()
        request = rf.get("/dummy-url")
        request.user = None
        self.mixin.request = request
        self.mixin.patient = None

    def test_mh_name(self):
        assert self.mixin.mh_name == "diabetes"

    def test_model(self):
        model = self.mixin.model
        from django.apps import apps

        expected = apps.get_model("medhistorys", "diabetes")
        assert model == expected

    def test_get_context_data(self):
        context = self.mixin.get_context_data()
        assert context["foo"] == "bar"
        assert context["mhtype"] == MHTypes.DIABETES

    def test_get_form_kwargs(self):
        kwargs = self.mixin.get_form_kwargs()
        # get_form_kwargs should NOT call super() on any other MRO classes
        # It is overwritten to avoid adding an instance to a non-ModelForm
        assert "bas" not in kwargs
        from django.apps import apps

        expected = apps.get_model("medhistorys", "diabetes")
        assert kwargs["model"] == expected
