from collections.abc import Sequence
from datetime import date
from typing import Any
from uuid import UUID

from factory import Faker
from factory import post_generation
from factory.django import DjangoModelFactory

from gouthelper_ninja.dateofbirths.tests.factories import DateOfBirthFactory
from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.ethnicitys.tests.factories import EthnicityFactory
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.tests.factories import GenderFactory
from gouthelper_ninja.profiles.tests.factories import PatientProfileFactory
from gouthelper_ninja.users.models import User


class UserFactory(DjangoModelFactory[User]):
    username = Faker("user_name")
    email = Faker("email")
    name = Faker("name")

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):  # noqa: FBT001
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        """Save again the instance if creating and at least one hook ran."""
        if create and results and not cls._meta.skip_postgeneration_save:
            # Some post-generation hooks ran, and may have modified us.
            instance.save()

    class Meta:
        model = User
        django_get_or_create = ["username"]


class PatientFactory(UserFactory):
    role = User.Roles.PSEUDOPATIENT

    @post_generation
    def dateofbirth(self, create: bool, extracted: date | str | None, **kwargs):  # noqa: FBT001
        if create:
            if extracted:
                kwargs["dateofbirth"] = (
                    extracted
                    if not isinstance(extracted, str)
                    else date(*map(int, extracted.split("-")))
                )
            DateOfBirthFactory(patient=self, **kwargs)

    @post_generation
    def ethnicity(
        self,
        create: bool,  # noqa: FBT001
        extracted: Ethnicitys | str | None,
        **kwargs,
    ) -> None:
        if create:
            if extracted:
                kwargs["ethnicity"] = (
                    Ethnicitys(extracted) if isinstance(extracted, str) else extracted
                )
            EthnicityFactory(patient=self, **kwargs)

    @post_generation
    def gender(self, create: bool, extracted: Genders | str | None, **kwargs) -> None:  # noqa: FBT001
        if not hasattr(self, "gender") and create:
            if extracted:
                kwargs["gender"] = (
                    Genders(extracted) if isinstance(extracted, str) else extracted
                )
            GenderFactory(patient=self, **kwargs)

    @post_generation
    def patientprofile(
        self,
        create: bool,  # noqa: FBT001
        extracted: User | str | UUID,
        **kwargs,
    ) -> None:
        if create:
            if extracted:
                kwargs["provider"] = (
                    extracted
                    if isinstance(extracted, User)
                    else User.objects.get(username=extracted)
                )
                # TODO: compute the correct provider_alias based on the provider
                kwargs["provider_alias"] = 1  # Default alias for the provider
            PatientProfileFactory(user=self, **kwargs)
