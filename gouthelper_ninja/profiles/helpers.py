from typing import TYPE_CHECKING

from django.apps import apps
from django.utils import timezone

from gouthelper_ninja.dateofbirths.querysets import annotate_patient_queryset_with_age
from gouthelper_ninja.users.querysets import age_gender_filter

if TYPE_CHECKING:
    from uuid import UUID

    from django.config.auth import get_user_model

    from gouthelper_ninja.genders.choices import Genders

    User = get_user_model()


def get_provider_alias(
    provider_id: "UUID",
    age: int,
    gender: "Genders",
) -> int | None:
    queryset = annotate_patient_queryset_with_age(
        qs=apps.get_model("users.Patient")
        .objects.select_related(
            "dateofbirth",
            "gender",
            "patientprofile__provider",
        )
        .filter(
            patientprofile__provider_id=provider_id,
            created__date=timezone.localdate(),
        ),
    )

    # Count of related patients with the same age, gender, and created date
    alias_conflicts = age_gender_filter(
        qs=queryset,
        age=age,
        gender=gender,
    ).count()

    return alias_conflicts + 1
