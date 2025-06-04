from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.config.auth import get_user_model

    from gouthelper_ninja.genders.choices import Genders

    User = get_user_model()


def get_provider_alias(
    provider: "User",
    age: int,
    gender: "Genders",
) -> int | None:
    return 1
