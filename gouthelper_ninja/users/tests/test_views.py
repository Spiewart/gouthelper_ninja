from http import HTTPStatus

import pytest
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.http import Http404
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
from gouthelper_ninja.goutdetails.forms import GoutDetailForm
from gouthelper_ninja.medhistorys.forms import MedHistoryForm
from gouthelper_ninja.users.forms import UserAdminChangeForm
from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.models import User
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory
from gouthelper_ninja.users.views import PatientCreateView
from gouthelper_ninja.users.views import PatientDeleteView
from gouthelper_ninja.users.views import PatientDetailView
from gouthelper_ninja.users.views import PatientProviderCreateView
from gouthelper_ninja.users.views import PatientUpdateView
from gouthelper_ninja.users.views import UserRedirectView
from gouthelper_ninja.users.views import UserUpdateView
from gouthelper_ninja.users.views import user_delete_view
from gouthelper_ninja.users.views import user_detail_view
from gouthelper_ninja.utils.helpers import get_str_attrs_dict
from gouthelper_ninja.utils.helpers import yearsago_date
from gouthelper_ninja.utils.tests.helpers import dummy_get_response
from gouthelper_ninja.utils.tests.helpers import print_response_errors

pytestmark = pytest.mark.django_db


class TestPatientCreateView(TestCase):
    """Tests for the PatientCreateView."""

    def setUp(self):
        self.provider = UserFactory()
        self.anon = AnonymousUser()
        self.rf = RequestFactory()
        self.data = {
            "dateofbirth": 70,
            "ethnicity": Ethnicitys.CAUCASIAN,
            "gender": Genders.FEMALE,
            "gout-history_of": False,
            "at_goal": True,
            "at_goal_long_term": True,
            "flaring": False,
            "on_ppx": True,
            "on_ult": True,
            "starting_ult": True,
            "menopause-history_of": True,
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

    def test__get_permission_required(self):
        assert not hasattr(self.get_view, "get_permission_required")

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
        assert "gout_form" in context
        assert isinstance(context["gout_form"], MedHistoryForm)
        assert "goutdetail_form" in context
        assert isinstance(context["goutdetail_form"], GoutDetailForm)

    def test__patient(self):
        assert self.get_view.patient is None

    def test__provider(self):
        assert not hasattr(self.get_view, "provider")

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
        print_response_errors(response)
        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == HTTPStatus.FOUND

        assert Patient.objects.count() == num_patients + 1

        patient = Patient.objects.order_by("created").last()
        assert response.url == reverse(
            "users:patient-detail",
            kwargs={"patient": patient.id},
        )
        assert hasattr(patient, "goutdetail")
        assert patient.goutdetail.at_goal == self.data["at_goal"]
        assert patient.goutdetail.at_goal_long_term == self.data["at_goal_long_term"]
        assert patient.goutdetail.flaring == self.data["flaring"]
        assert patient.goutdetail.on_ppx == self.data["on_ppx"]
        assert patient.goutdetail.on_ult == self.data["on_ult"]
        assert patient.goutdetail.starting_ult == self.data["starting_ult"]

        assert patient.menopause
        assert patient.menopause.history_of == self.data["menopause-history_of"]

    def test__post_with_errors(self):
        # Test with invalid data
        invalid_data = self.data.copy()
        invalid_data["dateofbirth"] = "invalid_date"

        self.post_view.request.POST = invalid_data

        SessionMiddleware(dummy_get_response).process_request(self.post)
        MessageMiddleware(dummy_get_response).process_request(self.post)

        response = self.post_view.post(self.post)

        assert response.status_code == HTTPStatus.OK
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
        assert "gout_form" in response.context_data
        assert not response.context_data["gout_form"].errors
        assert "goutdetail_form" in response.context_data
        assert not response.context_data["goutdetail_form"].errors

    def test__permission(self):
        """Test that the view can be accessed by anyone when there is no
        provider specified."""

        self.get.user = self.anon

        assert PatientCreateView.as_view()(self.get)

        self.get.user = PatientFactory()

        assert PatientCreateView.as_view()(self.get)

        self.get.user = self.provider

        assert PatientCreateView.as_view()(self.get)

        self.post.user = self.anon
        self.post.htmx = False
        SessionMiddleware(dummy_get_response).process_request(self.post)
        MessageMiddleware(dummy_get_response).process_request(self.post)

        assert PatientCreateView.as_view()(self.post)

        self.post.user = PatientFactory()

        assert PatientCreateView.as_view()(self.post)

        self.post.user = self.provider

        assert PatientCreateView.as_view()(self.post)


class TestPatientProviderCreateView(TestCase):
    """Tests for the PatientCreateView."""

    def setUp(self):
        self.provider = UserFactory()
        self.anon = AnonymousUser()
        self.rf = RequestFactory()
        self.data = {
            "dateofbirth": 70,
            "ethnicity": Ethnicitys.CAUCASIAN,
            "gender": Genders.FEMALE,
            "gout-history_of": False,
            "at_goal": True,
            "at_goal_long_term": True,
            "flaring": False,
            "on_ppx": True,
            "on_ult": True,
            "starting_ult": True,
            "menopause-history_of": True,
        }

        self.get = self.rf.get(
            reverse(
                "users:provider-patient-create",
                kwargs={"provider": self.provider.username},
            ),
        )

        self.get.user = self.provider
        self.get_view = PatientProviderCreateView(
            kwargs={"provider": self.provider.username},
        )
        self.get_view.request = self.get
        self.get_view.object = None

        self.post = self.rf.post(
            reverse(
                "users:provider-patient-create",
                kwargs={"provider": self.provider.username},
            ),
            data=self.data,
        )
        self.post.user = self.provider
        self.post_view = PatientProviderCreateView(
            kwargs={"provider": self.provider.username},
        )
        self.post_view.request = self.post
        self.post_view.request.htmx = (
            False  # Set HTMX to False to avoid HTMX-specific behavior in the test
        )
        self.post_view.object = None

    def test__get_permission_required(self):
        assert self.get_view.get_permission_required() == (
            "users.can_add_provider_patient",
        )

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
        assert isinstance(context["form"], PatientProviderCreateView.form_class)
        assert context["form"].initial == {}
        assert "patient_form" not in context
        assert "dateofbirth_form" in context
        assert isinstance(context["dateofbirth_form"], DateOfBirthForm)
        assert "ethnicity_form" in context
        assert isinstance(context["ethnicity_form"], EthnicityForm)
        assert "gender_form" in context
        assert isinstance(context["gender_form"], GenderForm)
        assert "gout_form" in context
        assert isinstance(context["gout_form"], MedHistoryForm)
        assert "goutdetail_form" in context
        assert isinstance(context["goutdetail_form"], GoutDetailForm)

    def test__patient(self):
        assert self.get_view.patient is None

    def test__provider(self):
        assert self.get_view.provider == self.provider

    def test__str_attrs(self):
        assert self.get_view.str_attrs
        assert isinstance(self.get_view.str_attrs, dict)
        assert self.get_view.str_attrs == get_str_attrs_dict(
            None,
            self.get_view.request_user,
        )

    def test__get(self):
        response = self.get_view.get(self.get)
        assert isinstance(response, HttpResponse)
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context_data
        assert isinstance(
            response.context_data["form"],
            PatientProviderCreateView.form_class,
        )
        assert "patient_form" not in response.context_data
        assert "dateofbirth_form" in response.context_data
        assert isinstance(response.context_data["dateofbirth_form"], DateOfBirthForm)
        assert "gender_form" in response.context_data
        assert isinstance(response.context_data["gender_form"], GenderForm)
        assert "ethnicity_form" in response.context_data
        assert isinstance(response.context_data["ethnicity_form"], EthnicityForm)
        assert "goutdetail_form" in response.context_data
        assert isinstance(response.context_data["goutdetail_form"], GoutDetailForm)

    def test__post(self):
        num_patients = Patient.objects.count()
        assert num_patients == 0

        SessionMiddleware(dummy_get_response).process_request(self.post)
        MessageMiddleware(dummy_get_response).process_request(self.post)

        response = self.post_view.post(self.post)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == HTTPStatus.FOUND

        patient = Patient.objects.order_by("created").last()
        assert response.url == reverse(
            "users:patient-detail",
            kwargs={"patient": patient.id},
        )

        assert Patient.objects.count() == num_patients + 1
        assert patient.patientprofile.provider == self.provider
        assert patient.patientprofile.provider_alias == num_patients + 1

        # Test that calling the view a second time, creating another identifical
        # patient, increments the provider alias
        response = self.post_view.post(self.post)
        assert response.status_code == HTTPStatus.FOUND

        assert Patient.objects.count() == num_patients + 2
        new_patient = Patient.objects.order_by("created").last()
        assert new_patient.patientprofile.provider == self.provider
        assert new_patient.patientprofile.provider_alias == num_patients + 2
        assert hasattr(new_patient, "goutdetail")
        assert new_patient.goutdetail.at_goal == self.data["at_goal"]
        assert (
            new_patient.goutdetail.at_goal_long_term == self.data["at_goal_long_term"]
        )
        assert new_patient.goutdetail.flaring == self.data["flaring"]
        assert new_patient.goutdetail.on_ppx == self.data["on_ppx"]
        assert new_patient.goutdetail.on_ult == self.data["on_ult"]
        assert new_patient.goutdetail.starting_ult == self.data["starting_ult"]
        assert new_patient.menopause
        assert new_patient.menopause.history_of == self.data["menopause-history_of"]

    def test__post_with_errors(self):
        # Test with invalid data
        invalid_data = self.data.copy()
        invalid_data["dateofbirth"] = "invalid_date"

        self.post_view.request.POST = invalid_data

        SessionMiddleware(dummy_get_response).process_request(self.post)
        MessageMiddleware(dummy_get_response).process_request(self.post)

        response = self.post_view.post(self.post)

        assert response.status_code == HTTPStatus.OK
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
        assert "goutdetail_form" in response.context_data
        assert not response.context_data["goutdetail_form"].errors

    def test__permission(self):
        """Test that the view can only be accessed by the provider
        specified in the URL kwargs."""
        self.get.user = self.anon

        kwargs = {"provider": self.provider.username}

        with pytest.raises(PermissionDenied):
            # Need to raise exception to test permissions when user is not authenticated
            PatientProviderCreateView.as_view(raise_exception=True)(self.get, **kwargs)

        self.get.user = PatientFactory()

        with pytest.raises(PermissionDenied):
            PatientProviderCreateView.as_view()(self.get, **kwargs)

        self.get.user = self.provider

        assert PatientProviderCreateView.as_view()(self.get, **kwargs)

        # Test POST request with an anonymous user who should not have permission
        self.post.user = self.anon
        self.post.htmx = False
        SessionMiddleware(dummy_get_response).process_request(self.post)
        MessageMiddleware(dummy_get_response).process_request(self.post)

        with pytest.raises(PermissionDenied):
            PatientProviderCreateView.as_view(raise_exception=True)(self.post, **kwargs)

        # Test POST request with a user who is not the provider
        # but is a Patient, which should not have permission
        self.post.user = PatientFactory()

        with pytest.raises(PermissionDenied):
            PatientProviderCreateView.as_view()(self.post, **kwargs)

        self.post.user = self.provider
        assert PatientProviderCreateView.as_view()(self.post, **kwargs)


class TestPatientDeleteView(TestCase):
    """Tests for the PatientDeleteView."""

    def setUp(self):
        self.rf = RequestFactory()
        self.provider = UserFactory()
        self.admin = UserFactory(role=User.Roles.ADMIN)
        self.patient = PatientFactory()
        self.patient_of_provider = PatientFactory(provider=self.provider)
        self.patient_with_creator = PatientFactory(creator=self.provider)
        self.unrelated_provider = UserFactory()
        self.anon = AnonymousUser()

    def _get_url(self, patient):
        return reverse("users:patient-delete", kwargs={"patient": patient.id})

    def _get_request(self, user, url):
        request = self.rf.get(url)
        request.user = user
        return request

    def _post_request(self, user, url):
        request = self.rf.post(url)
        request.user = user
        SessionMiddleware(dummy_get_response).process_request(request)
        MessageMiddleware(dummy_get_response).process_request(request)
        return request

    def test_get_request_shows_confirmation(self):
        """Test GET request to the delete confirmation page."""
        request = self._get_request(
            self.provider,
            self._get_url(self.patient_of_provider),
        )
        response = PatientDeleteView.as_view()(
            request,
            patient=self.patient_of_provider.id,
        )
        assert response.status_code == HTTPStatus.OK
        response = response.render()
        assert "Are you sure you want to delete" in response.content.decode()

    def test_post_deletes_patient_and_redirects(self):
        """Test POST request deletes the patient and redirects."""
        patient_to_delete = PatientFactory(provider=self.provider)
        patient_count = Patient.objects.count()

        request = self._post_request(self.provider, self._get_url(patient_to_delete))

        response = PatientDeleteView.as_view()(request, patient=patient_to_delete.id)

        assert Patient.objects.count() == patient_count - 1
        with pytest.raises(Patient.DoesNotExist):
            Patient.objects.get(id=patient_to_delete.id)

        assert response.status_code == HTTPStatus.FOUND
        assert response.url == reverse(
            "users:detail",
            kwargs={"username": self.provider.username},
        )

        messages_sent = [m.message for m in messages.get_messages(request)]
        assert "GoutPatient successfully deleted" in messages_sent

    def test_patient_deleting_themselves_redirects_to_home(self):
        """Test a patient deleting their own account redirects to home."""
        patient_to_delete = PatientFactory()
        patient_count = Patient.objects.count()

        request = self._post_request(
            patient_to_delete,
            self._get_url(patient_to_delete),
        )

        response = PatientDeleteView.as_view()(request, patient=patient_to_delete.id)

        assert Patient.objects.count() == patient_count - 1
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == reverse("contents:home")

    def test_permissions(self):
        """Test view permissions for deleting a patient."""
        patient = self.patient_of_provider
        url = self._get_url(patient)
        kwargs = {"patient": patient.id}

        # Anonymous user cannot delete
        request = self._post_request(self.anon, url)
        with pytest.raises(PermissionDenied):
            PatientDeleteView.as_view(raise_exception=True)(request, **kwargs)

        # Unrelated provider cannot delete
        request = self._post_request(self.unrelated_provider, url)
        with pytest.raises(PermissionDenied):
            PatientDeleteView.as_view(raise_exception=True)(request, **kwargs)

        # Patient cannot delete another patient with a provider
        other_patient = PatientFactory()
        request = self._post_request(other_patient, url)
        with pytest.raises(PermissionDenied):
            PatientDeleteView.as_view(raise_exception=True)(request, **kwargs)

        # Patient's provider can delete
        request = self._post_request(self.provider, url)
        response = PatientDeleteView.as_view()(request, **kwargs)
        assert response.status_code == HTTPStatus.FOUND

        # Patient with creator
        patient_c = PatientFactory(creator=self.provider)
        url_c = self._get_url(patient_c)
        kwargs_c = {"patient": patient_c.id}

        # Creator can delete
        request = self._post_request(self.provider, url_c)
        response = PatientDeleteView.as_view()(request, **kwargs_c)
        assert response.status_code == HTTPStatus.FOUND

        # Admin can delete any patient
        patient_a = PatientFactory(provider=self.unrelated_provider)
        url_a = self._get_url(patient_a)
        kwargs_a = {"patient": patient_a.id}
        request = self._post_request(self.admin, url_a)
        response = PatientDeleteView.as_view()(request, **kwargs_a)
        assert response.status_code == HTTPStatus.FOUND


class TestPatientDetailView(TestCase):
    def setUp(self):
        self.provider = UserFactory()
        self.patient = PatientFactory()

        self.rf = RequestFactory()
        self.get = self.rf.get(
            reverse("users:patient-detail", kwargs={"patient": self.patient.id}),
        )
        self.get.user = self.provider
        self.kwargs = {"patient": self.patient.id}
        self.get_view = PatientDetailView(kwargs=self.kwargs)
        self.get_view.request = self.get

    def test__get_permission_object(self):
        assert self.get_view.get_permission_object() == self.patient

    def test__patient(self):
        assert isinstance(self.get_view.patient, Patient)
        assert self.get_view.patient.pk == self.patient.pk

    def test__get_object(self):
        assert self.get_view.get_object() == self.patient

        self.get_view.kwargs.update({"patient": 9999})
        with pytest.raises(Http404):
            self.get_view.get_object()

        self.get_view.kwargs.pop("patient", None)
        with pytest.raises(AttributeError):
            self.get_view.get_object()

    def test__get(self):
        response = self.get_view.get(self.get)
        assert isinstance(response, HttpResponse)
        assert response.status_code == HTTPStatus.OK
        assert "object" in response.context_data
        assert response.context_data["object"] == self.patient

    def test__permission(self):
        self.get.user = AnonymousUser()

        assert PatientDetailView.as_view()(self.get, **self.kwargs)

        self.get.user = PatientFactory()

        assert PatientDetailView.as_view()(self.get, **self.kwargs)

        provider_patient = PatientFactory(provider=self.provider)

        get_with_provider = self.rf.get(
            reverse("users:patient-detail", kwargs={"patient": provider_patient.id}),
        )
        get_with_provider.user = AnonymousUser()

        with pytest.raises(PermissionDenied):
            PatientDetailView.as_view(raise_exception=True)(
                get_with_provider,
                patient=provider_patient.id,
            )

        patient_created_by_provider = PatientFactory(creator=self.provider)

        get_with_creator = self.rf.get(
            reverse(
                "users:patient-detail",
                kwargs={"patient": patient_created_by_provider.id},
            ),
        )

        get_with_creator.user = AnonymousUser()

        assert PatientDetailView.as_view()(
            get_with_creator,
            patient=patient_created_by_provider.id,
        )

        most_recent_history = patient_created_by_provider.history.first()
        most_recent_history.history_user = self.provider
        most_recent_history.save()

        with pytest.raises(PermissionDenied):
            PatientDetailView.as_view(raise_exception=True)(
                get_with_creator,
                patient=patient_created_by_provider.id,
            )


class TestPatientUpdateView(TestCase):
    def setUp(self):
        self.provider = UserFactory()
        self.rf = RequestFactory()
        self.provider = UserFactory()
        self.patient = PatientFactory(
            dateofbirth=50,
            ethnicity=Ethnicitys.AFRICANAMERICAN,
            gender=Genders.MALE,
        )
        self.data = {
            "dateofbirth": 70,
            "ethnicity": Ethnicitys.CAUCASIAN,
            "gender": Genders.FEMALE,
            "gout-history_of": False,
            "at_goal": True,
            "at_goal_long_term": True,
            "flaring": not self.patient.goutdetail.flaring,
            "on_ppx": True,
            "on_ult": True,
            "starting_ult": True,
            "menopause-history_of": True,
            "id": self.patient.id,
        }
        self.patient_with_provider = PatientFactory(
            dateofbirth=50,
            ethnicity=Ethnicitys.AFRICANAMERICAN,
            gender=Genders.MALE,
            provider=self.provider,
        )

        self.patient_kwargs = {"patient": self.patient.id}
        self.get = self.rf.get(
            reverse("users:patient-update", kwargs=self.patient_kwargs),
        )
        self.get.user = self.provider
        self.get_view = PatientUpdateView()
        self.get_view.kwargs = self.patient_kwargs
        self.get_view.object = self.patient
        self.get_view.request = self.get

        self.post = self.rf.post(
            reverse("users:patient-update", kwargs=self.patient_kwargs),
            data=self.data,
        )
        self.post.user = self.provider
        self.post_view = PatientUpdateView(kwargs=self.patient_kwargs)

        self.post_view.request = self.post
        self.post_view.request.htmx = (
            False  # Set HTMX to False to avoid HTMX-specific behavior in the test
        )

    def test__get(self):
        response = self.get_view.get(self.get)
        assert isinstance(response, HttpResponse)
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context_data
        assert isinstance(response.context_data["form"], PatientUpdateView.form_class)
        assert "dateofbirth_form" in response.context_data
        assert isinstance(response.context_data["dateofbirth_form"], DateOfBirthForm)
        assert response.context_data["dateofbirth_form"].initial == {
            "dateofbirth": self.patient.dateofbirth.dateofbirth,
        }
        assert "ethnicity_form" in response.context_data
        assert isinstance(response.context_data["ethnicity_form"], EthnicityForm)
        assert response.context_data["ethnicity_form"].initial == {
            "ethnicity": self.patient.ethnicity.ethnicity,
        }
        assert "gender_form" in response.context_data
        assert isinstance(response.context_data["gender_form"], GenderForm)
        assert response.context_data["gender_form"].initial == {
            "gender": self.patient.gender.gender,
        }
        assert "gout_form" in response.context_data
        assert isinstance(response.context_data["gout_form"], MedHistoryForm)
        assert response.context_data["gout_form"].initial == {
            "history_of": self.patient.gout.history_of,
        }
        assert "goutdetail_form" in response.context_data
        assert isinstance(response.context_data["goutdetail_form"], GoutDetailForm)
        assert response.context_data["goutdetail_form"].initial == {
            "at_goal": self.patient.goutdetail.at_goal,
            "at_goal_long_term": self.patient.goutdetail.at_goal_long_term,
            "flaring": self.patient.goutdetail.flaring,
            "on_ppx": self.patient.goutdetail.on_ppx,
            "on_ult": self.patient.goutdetail.on_ult,
            "starting_ult": self.patient.goutdetail.starting_ult,
        }
        assert "object" in response.context_data
        assert response.context_data["object"] == self.patient

    def test__post(self):
        num_patients = Patient.objects.count()

        SessionMiddleware(dummy_get_response).process_request(self.post)
        MessageMiddleware(dummy_get_response).process_request(self.post)

        response = self.post_view.post(self.post)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == HTTPStatus.FOUND

        assert response.url == reverse(
            "users:patient-detail",
            kwargs={"patient": self.patient.id},
        )

        assert Patient.objects.count() == num_patients

        self.patient.refresh_from_db()
        assert self.patient.dateofbirth.dateofbirth == yearsago_date(
            self.data["dateofbirth"],
        )
        assert self.patient.ethnicity.ethnicity == self.data["ethnicity"]
        assert self.patient.gender.gender == self.data["gender"]

        # Test that the Patient's gout history is updated correctly
        assert self.patient.gout.history_of == self.data["gout-history_of"]

        # Test that the goutdetail flaring field is updated correctly
        assert self.patient.goutdetail.flaring == self.data["flaring"]

    def test__post_with_errors(self):
        # Test with invalid data
        invalid_data = self.data.copy()
        invalid_data["dateofbirth"] = "invalid_date"

        self.post_view.request.POST = invalid_data

        SessionMiddleware(dummy_get_response).process_request(self.post)
        MessageMiddleware(dummy_get_response).process_request(self.post)

        response = self.post_view.post(self.post)

        assert response.status_code == HTTPStatus.OK
        assert isinstance(response, HttpResponseRedirect) is False
        assert isinstance(response, HttpResponse)
        assert "form" in response.context_data
        assert not response.context_data["form"].errors
        assert "dateofbirth_form" in response.context_data
        assert response.context_data["dateofbirth_form"].errors

    def test__permission(self):
        """Test that the view can only be accessed by the patient,
        the patient's provider, the patient's creator, or an admin."""

        anon = AnonymousUser()
        # Test with AnonymousUser
        self.get.user = anon

        assert PatientUpdateView.as_view(raise_exception=True)(
            self.get,
            **self.patient_kwargs,
        )

        patient_with_provider_kwargs = {"patient": self.patient_with_provider.id}

        with pytest.raises(PermissionDenied):
            PatientUpdateView.as_view(raise_exception=True)(
                self.get,
                **patient_with_provider_kwargs,
            )

        # Test with a random patient
        self.get.user = PatientFactory()

        assert PatientUpdateView.as_view(raise_exception=True)(
            self.get,
            **self.patient_kwargs,
        )

        with pytest.raises(PermissionDenied):
            PatientUpdateView.as_view(raise_exception=True)(
                self.get,
                **patient_with_provider_kwargs,
            )

        # Test with the patient
        self.get.user = self.provider
        assert PatientUpdateView.as_view()(self.get, **patient_with_provider_kwargs)

        # Test with the patient's provider

        self.get.user = self.provider
        assert PatientUpdateView.as_view()(self.get, **patient_with_provider_kwargs)

        # Test with a random provider
        self.get.user = UserFactory()
        with pytest.raises(PermissionDenied):
            PatientUpdateView.as_view(raise_exception=True)(
                self.get,
                **patient_with_provider_kwargs,
            )

        # Test with the patient's creator
        patient_created_by_provider = PatientFactory(creator=self.provider)
        patient_created_by_provider_kwargs = {"patient": patient_created_by_provider.id}
        self.get.user = self.provider
        assert PatientUpdateView.as_view()(
            self.get,
            **patient_created_by_provider_kwargs,
        )

        # Test with a random user
        self.get.user = UserFactory()
        with pytest.raises(PermissionDenied):
            PatientUpdateView.as_view(raise_exception=True)(
                self.get,
                **patient_created_by_provider_kwargs,
            )

        self.get.user = patient_created_by_provider

        assert PatientUpdateView.as_view()(
            self.get,
            **patient_created_by_provider_kwargs,
        )

        self.get.user = anon

        with pytest.raises(PermissionDenied):
            PatientUpdateView.as_view(raise_exception=True)(
                self.get,
                **patient_created_by_provider_kwargs,
            )

        self.get.user = UserFactory(role=User.Roles.ADMIN)
        assert PatientUpdateView.as_view()(
            self.get,
            **patient_created_by_provider_kwargs,
        )


class TestUserUpdateView:
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
        SessionMiddleware(dummy_get_response).process_request(request)
        MessageMiddleware(dummy_get_response).process_request(request)
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
        with pytest.raises(PermissionDenied):
            response = user_detail_view(request, username=user.username)

        response = user_detail_view(request, username=request.user.username)
        assert response.status_code == HTTPStatus.OK

    def test_not_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = AnonymousUser()
        response = user_detail_view(request, username=user.username)
        login_url = reverse(settings.LOGIN_URL)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == f"{login_url}?next=/fake-url/"


class TestUserDeleteView:
    def test_get_request_shows_confirmation_page(self, user: User, rf: RequestFactory):
        """Test GET request by an authenticated user shows confirmation page."""
        url = reverse("users:delete")
        request = rf.get(url)
        request.user = user
        response = user_delete_view(request)

        assert response.status_code == HTTPStatus.OK
        response.render()
        # Default Django DeleteView template contains this text
        assert b"Are you sure you want to delete" in response.content

    def test_get_request_unauthenticated_redirects_to_login(self, rf: RequestFactory):
        """Test GET request by an unauthenticated user redirects to login."""
        url = reverse("users:delete")
        request = rf.get(url)
        request.user = AnonymousUser()
        response = user_delete_view(request)

        login_url = reverse(settings.LOGIN_URL)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == f"{login_url}?next={url}"

    def test_post_deletes_user_and_redirects(self, user: User, rf: RequestFactory):
        """Test POST request deletes the user and redirects home with a message."""
        url = reverse("users:delete")
        request = rf.post(url)
        request.user = user

        # Add middleware for messages
        SessionMiddleware(dummy_get_response).process_request(request)
        MessageMiddleware(dummy_get_response).process_request(request)

        user_count = User.objects.count()

        response = user_delete_view(request)

        assert User.objects.count() == user_count - 1
        with pytest.raises(User.DoesNotExist):
            User.objects.get(pk=user.pk)

        assert response.status_code == HTTPStatus.FOUND
        assert response.url == reverse("contents:home")

        messages_sent = [m.message for m in messages.get_messages(request)]
        assert "Account successfully deleted" in messages_sent


class TestUserViewPermissions(TestCase):
    def setUp(self):
        self.provider = UserFactory()
        self.patient = PatientFactory()
        self.patient_with_provider = PatientFactory(provider=self.provider)
        self.patient_with_creator = PatientFactory(creator=self.provider)
        self.another_provider = UserFactory()
        self.anon = AnonymousUser()
        self.admin = UserFactory(role=User.Roles.ADMIN)

    def test__delete_permissions(self):
        # Test that an unlogged in user is redirected to the login page
        url = reverse("users:delete")
        response = self.client.get(url)
        login_url = reverse(settings.LOGIN_URL)

        assert response.status_code == HTTPStatus.FOUND
        assert response.url == f"{login_url}?next={url}"

        # Test that the logged in user can access their own delete view
        self.client.force_login(self.provider)
        response = self.client.get(url)
        assert response.status_code == HTTPStatus.OK
        response = self.client.post(url)
        assert response.status_code == HTTPStatus.FOUND

        # Test that the anonymous Patient can delete themselves
        self.client.force_login(self.patient)
        response = self.client.get(url)
        assert response.status_code == HTTPStatus.OK
        response = self.client.post(url)
        assert response.status_code == HTTPStatus.FOUND

        # Test that an Admin can delete themself
        self.client.force_login(self.admin)
        response = self.client.get(url)
        assert response.status_code == HTTPStatus.OK
        response = self.client.post(url)
        assert response.status_code == HTTPStatus.FOUND

    def test__detail_permissions(self):
        # Test that an unlogged in user can't access the detail view
        url = reverse("users:detail", kwargs={"username": self.provider.username})
        response = self.client.get(url)
        login_url = reverse(settings.LOGIN_URL)

        assert response.status_code == HTTPStatus.FOUND
        assert response.url == f"{login_url}?next={url}"

        # Test that the logged in user can access their own detail view
        self.client.force_login(self.provider)
        response = self.client.get(url)
        assert response.status_code == HTTPStatus.OK

        # Test that the logged in user can't access another user's detail view
        another_user = UserFactory()
        another_url = reverse(
            "users:detail",
            kwargs={"username": another_user.username},
        )
        response = self.client.get(another_url)
        assert response.status_code == HTTPStatus.FORBIDDEN

        # Test that the logged in patient can access their own detail view
        self.client.force_login(self.patient)
        patient_url = reverse(
            "users:detail",
            kwargs={"username": self.patient.username},
        )
        response = self.client.get(patient_url)
        assert response.status_code == HTTPStatus.OK

        # Test that an Admin can access any user's detail view
        self.client.force_login(self.admin)
        response = self.client.get(url)
        assert response.status_code == HTTPStatus.OK
        response = self.client.get(another_url)
        assert response.status_code == HTTPStatus.OK
        response = self.client.get(patient_url)
        assert response.status_code == HTTPStatus.OK

    def test__update_permissions(self):
        # Test that an unlogged in user can't access the update view
        url = reverse("users:update")
        response = self.client.get(url)
        login_url = reverse(settings.LOGIN_URL)

        assert response.status_code == HTTPStatus.FOUND
        assert response.url == f"{login_url}?next={url}"

        # Test that the logged in user can access their own update view
        self.client.force_login(self.provider)
        response = self.client.get(url)
        assert response.status_code == HTTPStatus.OK
        response = self.client.post(url, data={"username": "new_username"})
        assert response.status_code == HTTPStatus.FOUND
