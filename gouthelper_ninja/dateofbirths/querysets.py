from typing import TYPE_CHECKING

from django.db.models import F
from django.db.models import Func
from django.db.models import IntegerField
from django.db.models import Value
from django.utils import timezone

if TYPE_CHECKING:
    from django.db.models import QuerySet


def annotate_patient_queryset_with_age(qs: "QuerySet") -> "QuerySet":
    """Method that takes a QuerySet of Patients and annotates it with
    their age based on their date of birth."""

    return qs.annotate(
        age=Func(
            Value("year"),
            Func(
                Value(timezone.now().date()),
                F("dateofbirth__dateofbirth"),
                function="age",
            ),
            function="date_part",
            output_field=IntegerField(),
        ),
    )
