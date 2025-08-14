from typing import TYPE_CHECKING
from typing import Union

from gouthelper_ninja.constants import MAX_MENOPAUSE_AGE
from gouthelper_ninja.constants import MIN_MENOPAUSE_AGE
from gouthelper_ninja.genders.choices import Genders

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from gouthelper_ninja.medhistorys.choices import MHTypes
    from gouthelper_ninja.medhistorys.models import MedHistory


def menopause_required(
    gender: Genders,
    age: int,
) -> bool:
    """Returns True if menopause is required for the provided
    gender and age."""
    return (
        age >= MIN_MENOPAUSE_AGE
        and age < MAX_MENOPAUSE_AGE
        and gender == Genders.FEMALE
    )


def search_medhistorys_by_mhtype(
    medhistorys: Union[list["MedHistory"], "QuerySet[MedHistory]"],
    mhtype: "MHTypes",
) -> Union["MedHistory", None]:
    """Iterates through a list or QuerySet of MedHistory instances
    and returns the first MedHistory instance that matches the given type."""

    return (
        next(
            iter(
                medhistory for medhistory in medhistorys if medhistory.mhtype == mhtype
            ),
            None,
        )
        if medhistorys
        else None
    )
