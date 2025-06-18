import pytest
from django.contrib.auth import get_user_model

from gouthelper_ninja.dateofbirths.querysets import annotate_patient_queryset_with_age
from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.utils.helpers import age_calc

User = get_user_model()
pytestmark = pytest.mark.django_db


def test__annotate_with_age(patient: "Patient"):
    qs = annotate_patient_queryset_with_age(Patient.objects.filter(id=patient.id))

    annotated_patient = qs.get()

    assert hasattr(annotated_patient, "age")
    assert isinstance(annotated_patient.age, int)
    assert annotated_patient.age == age_calc(annotated_patient.dateofbirth.dateofbirth)
