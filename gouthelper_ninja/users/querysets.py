from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from gouthelper_ninja.genders.choices import Genders


def age_gender_filter(qs: "QuerySet", age: int, gender: "Genders") -> "QuerySet":
    """Filters a queryset of Patients by age and gender. Requires
    that the queryset has been annotated with age"""

    return qs.filter(
        age=age,
        gender__gender=gender,
    )


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
