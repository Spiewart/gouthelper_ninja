from http import HTTPStatus

import pytest
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.http import Http404
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
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory
from gouthelper_ninja.users.views import PatientCreateView
from gouthelper_ninja.users.views import PatientDetailView
from gouthelper_ninja.users.views import PatientProviderCreateView
from gouthelper_ninja.users.views import PatientUpdateView
from gouthelper_ninja.users.views import UserRedirectView
from gouthelper_ninja.users.views import UserUpdateView
from gouthelper_ninja.users.views import user_detail_view
from gouthelper_ninja.utils.helpers import get_str_attrs_dict
from gouthelper_ninja.utils.helpers import yearsago_date
from gouthelper_ninja.utils.test_helpers import RESPONSE_REDIRECT
from gouthelper_ninja.utils.test_helpers import RESPONSE_SUCCESS
from gouthelper_ninja.utils.test_helpers import dummy_get_response

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

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == RESPONSE_REDIRECT

        patient = Patient.objects.order_by("created").last()
        assert response.url == reverse(
            "users:patient-detail",
            kwargs={"patient": patient.id},
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

        assert response.status_code == RESPONSE_SUCCESS
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
        assert response.status_code == RESPONSE_SUCCESS
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

    def test__post(self):
        num_patients = Patient.objects.count()
        assert num_patients == 0

        SessionMiddleware(dummy_get_response).process_request(self.post)
        MessageMiddleware(dummy_get_response).process_request(self.post)

        response = self.post_view.post(self.post)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == RESPONSE_REDIRECT

        patient = Patient.objects.order_by("created").last()
        assert response.url == reverse(
            "users:patient-detail",
            kwargs={"patient": patient.id},
        )

        assert Patient.objects.count() == num_patients + 1
        assert patient.provider == self.provider
        assert patient.profile.provider_alias == num_patients + 1

        # Test that calling the view a second time, creating another identifical
        # patient, increments the provider alias
        response = self.post_view.post(self.post)
        assert response.status_code == RESPONSE_REDIRECT

        assert Patient.objects.count() == num_patients + 2
        new_patient = Patient.objects.order_by("created").last()
        assert new_patient.provider == self.provider
        assert new_patient.profile.provider_alias == num_patients + 2

    def test__post_with_errors(self):
        # Test with invalid data
        invalid_data = self.data.copy()
        invalid_data["dateofbirth"] = "invalid_date"

        self.post_view.request.POST = invalid_data

        SessionMiddleware(dummy_get_response).process_request(self.post)
        MessageMiddleware(dummy_get_response).process_request(self.post)

        response = self.post_view.post(self.post)

        assert response.status_code == RESPONSE_SUCCESS
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
        assert response.status_code == RESPONSE_SUCCESS
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

        patient_created_by_provider = PatientFactory()

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
        assert response.status_code == RESPONSE_SUCCESS
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
        assert "object" in response.context_data
        assert response.context_data["object"] == self.patient

    def test__post(self):
        num_patients = Patient.objects.count()

        SessionMiddleware(dummy_get_response).process_request(self.post)
        MessageMiddleware(dummy_get_response).process_request(self.post)

        response = self.post_view.post(self.post)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == RESPONSE_REDIRECT

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
        patient_created_by_provider = PatientFactory()
        most_recent_history = patient_created_by_provider.history.first()
        most_recent_history.history_user = self.provider
        most_recent_history.save()
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
