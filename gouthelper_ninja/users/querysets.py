from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet


def patientprofile_qs(qs: "QuerySet") -> "QuerySet":
    """Selects related PatientProfile instances for a queryset."""

    return qs.select_related("patientprofile__provider")


def patient_patientprofile_provider_qs(qs: "QuerySet") -> "QuerySet":
    """Selects related Patiend, PatientProfile, and Provider."""

    return qs.select_related(
        "patient__patientprofile__provider",
    )


def patient_qs(qs: "QuerySet") -> "QuerySet":
    """Selects related DateOfBirth, Ethnicity, and Gender models for a
    Patient and PatientProfile queryset."""

    return patientprofile_qs(qs).select_related(
        "dateofbirth",
        "ethnicity",
        "gender",
    )
