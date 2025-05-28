from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet


def patientprofile_qs(qs: "QuerySet") -> "QuerySet":
    """Selects related PatientProfile instances for a queryset."""

    return qs.select_related("patientprofile__provider")


def patient_update_qs(qs: "QuerySet") -> "QuerySet":
    """Selects related DateOfBirth, Ethnicity, and Gender models for a
    Patient and PatientProfile queryset."""

    return patientprofile_qs(qs).select_related(
        "dateofbirth",
        "ethnicity",
        "gender",
    )
