from django.urls import resolve
from django.urls import reverse

from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.medhistorys.views import MedHistoryCreateView
from gouthelper_ninja.medhistorys.views import MedHistoryUpdateView


def test_create_url_resolves():
    # Example UUID and mhtype for testing
    patient_uuid = "123e4567-e89b-12d3-a456-426614174000"
    mhtype = MHTypes.DIABETES
    url = reverse(
        "medhistorys:create",
        kwargs={"patient": patient_uuid, "mhtype": mhtype},
    )
    assert resolve(url).func.view_class == MedHistoryCreateView


def test_update_url_resolves():
    pk = "123e4567-e89b-12d3-a456-426614174000"
    url = reverse("medhistorys:update", kwargs={"pk": pk})
    assert resolve(url).func.view_class == MedHistoryUpdateView
