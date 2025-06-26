import pytest
from django.urls import resolve
from django.urls import reverse

from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.models import User

pytestmark = pytest.mark.django_db


# User URLs
def test_detail(user: User):
    """Tests reversing and resolving the user-detail URL."""
    assert (
        reverse("users:detail", kwargs={"username": user.username})
        == f"/users/{user.username}/"
    )
    assert resolve(f"/users/{user.username}/").view_name == "users:detail"


def test_update():
    """Tests reversing and resolving the user-update URL."""
    assert reverse("users:update") == "/users/~update/"
    assert resolve("/users/~update/").view_name == "users:update"


def test_redirect():
    """Tests reversing and resolving the user-redirect URL."""
    assert reverse("users:redirect") == "/users/~redirect/"
    assert resolve("/users/~redirect/").view_name == "users:redirect"


# Patient URLs
def test_patient_create():
    """Tests reversing and resolving the patient-create URL."""
    assert reverse("users:patient-create") == "/users/patients/create/"
    assert resolve("/users/patients/create/").view_name == "users:patient-create"


def test_provider_patient_create(provider: User):
    """Tests reversing and resolving the provider-patient-create URL."""
    url = reverse(
        "users:provider-patient-create",
        kwargs={"provider": provider.username},
    )
    resolved_path = f"/users/patients/provider-create/{provider.username}/"

    assert url == resolved_path
    assert resolve(resolved_path).view_name == "users:provider-patient-create"


def test_patient_detail(patient: Patient):
    """Tests reversing and resolving the patient-detail URL."""
    assert (
        reverse("users:patient-detail", kwargs={"patient": patient.id})
        == f"/users/patients/{patient.id}/"
    )
    assert resolve(f"/users/patients/{patient.id}/").view_name == "users:patient-detail"


def test_patient_update(patient: Patient):
    """Tests reversing and resolving the patient-update URL."""
    assert (
        reverse("users:patient-update", kwargs={"patient": patient.id})
        == f"/users/patients/{patient.id}/update/"
    )
    assert (
        resolve(f"/users/patients/{patient.id}/update/").view_name
        == "users:patient-update"
    )


def test_patient_delete(patient: Patient):
    """Tests reversing and resolving the patient-delete URL."""
    assert (
        reverse("users:patient-delete", kwargs={"patient": patient.id})
        == f"/users/patients/{patient.id}/delete/"
    )
    assert (
        resolve(f"/users/patients/{patient.id}/delete/").view_name
        == "users:patient-delete"
    )
