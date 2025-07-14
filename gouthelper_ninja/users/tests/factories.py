from collections.abc import Sequence
from datetime import date
from typing import Any
from typing import Literal
from uuid import UUID

from factory import Faker
from factory import post_generation
from factory.django import DjangoModelFactory
from ninja import Schema

from gouthelper_ninja.dateofbirths.tests.factories import DateOfBirthFactory
from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.ethnicitys.tests.factories import EthnicityFactory
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.tests.factories import GenderFactory
from gouthelper_ninja.goutdetails.tests.factories import GoutDetailFactory
from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.medhistorys.tests.factories import MedHistoryFactory
from gouthelper_ninja.profiles.helpers import get_provider_alias
from gouthelper_ninja.profiles.tests.factories import PatientProfileFactory
from gouthelper_ninja.users.models import User
from gouthelper_ninja.utils.helpers import age_calc
from gouthelper_ninja.utils.helpers import yearsago_date


class UserFactory(DjangoModelFactory[User]):
    username = Faker("user_name")
    email = Faker("email")
    name = Faker("name")

    @post_generation
    def password(
        self,
        create: Literal[True, False],
        extracted: Sequence[Any],
        **kwargs,
    ):
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
    def dateofbirth(
        self,
        create: Literal[True, False],
        extracted: date | str | None | Literal[False] = None,
        **kwargs,
    ):
        if create:
            if extracted is False:
                # If extracted is False, do not create a DateOfBirth
                return
            # If extracted is not None or True, it must be a date or age
            if extracted is not None:
                if isinstance(extracted, int):
                    # If extracted is an int, assume it's a number of years ago
                    extracted = yearsago_date(extracted)
                elif isinstance(extracted, str):
                    # If extracted is a string,
                    # assume it's a date in "YYYY-MM-DD" format
                    extracted = date(*map(int, extracted.split("-")))
                kwargs["dateofbirth"] = extracted
            DateOfBirthFactory(patient=self, **kwargs)

    @post_generation
    def ethnicity(
        self,
        create: Literal[True, False],
        extracted: Ethnicitys | str | None | Literal[False] = None,
        **kwargs,
    ) -> None:
        if create:
            # If extracted is False, do not create
            if extracted is False:
                return
            if extracted is not None:
                kwargs["ethnicity"] = (
                    Ethnicitys(extracted) if isinstance(extracted, str) else extracted
                )
            EthnicityFactory(patient=self, **kwargs)

    @post_generation
    def gender(
        self,
        create: Literal[True, False],
        extracted: Genders | str | None | Literal[False] = None,
        **kwargs,
    ) -> None:
        if create:
            if extracted is False:
                # If extracted is False, do not create
                return
            # Cannot check for Truth because values of Genders include 0
            if extracted is not None:
                kwargs["gender"] = (
                    Genders(extracted) if isinstance(extracted, str) else extracted
                )
            GenderFactory(patient=self, **kwargs)

    @post_generation
    def goutdetail(
        self,
        create: Literal[True, False],
        extracted: dict[str, Any] | None,
        **kwargs,
    ) -> None:
        """Post-generation hook to create a GoutDetail instance for the patient.
        args:
            extracted (dict[str, Any] | None):
                A dictionary of fields to set on the GoutDetail instance.
        """
        if create and extracted is not None:
            if extracted is not None:
                kwargs.update(extracted)
            GoutDetailFactory(
                patient=self,
                **kwargs,
            )

    @post_generation
    def medhistorys(
        self,
        create: Literal[True, False],
        extracted: dict[
            MHTypes,
            dict[str, Any] | bool,
        ]
        | Schema
        | None = None,
    ) -> None:
        """Post-generation hook to create MedHistory instances for the patient.
        args:
            extracted (dict[MHTypes, dict[str, Any] | bool | Schema] | None):
                A dictionary where keys are MHTypes and values are either
                a dictionary of fields to set or a boolean indicating whether to create
                the MedHistory with default values.
        """
        if create:
            if extracted is not None:
                if isinstance(extracted, Schema):
                    # If extracted is a Schema, convert to dict
                    extracted = extracted.dict()
                if MHTypes.GOUT not in extracted:
                    # If GOUT is not in the extracted, add it with default values
                    extracted[MHTypes.GOUT] = True
                for mhtype, fields in extracted.items():
                    # Check for fields set to None, which indicate
                    # MedHistorys that might otherwise be created
                    # but are intended to be skipped.
                    if fields is not None:
                        if isinstance(fields, bool):
                            # If fields is a boolean, create with default values and
                            # random history_of
                            MedHistoryFactory(
                                patient=self,
                                mhtype=mhtype,
                                history_of=fields,  # True or False
                            )
                        else:
                            # Otherwise, assume it's a dict of fields
                            MedHistoryFactory(
                                patient=self,
                                mhtype=mhtype,
                                **fields,
                            )
            else:
                MedHistoryFactory(
                    patient=self,
                    mhtype=MHTypes.GOUT,
                )

    @post_generation
    def provider(
        self,
        create: Literal[True, False],
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
                kwargs["provider_alias"] = get_provider_alias(
                    provider_id=kwargs["provider"].id,
                    age=kwargs.get(
                        "dateofbirth",
                        age_calc(self.dateofbirth.dateofbirth),
                    ),
                    gender=kwargs.get("gender", self.gender.gender),
                )
            PatientProfileFactory(user=self, **kwargs)

    @post_generation
    def creator(
        self,
        create: Literal[True, False],
        extracted: User | UUID | None = None,
        **kwargs,
    ) -> None:
        """Post-generation hook to set the creator of the patient, which is a
        a field on the User's history model.

        args:
            extracted (User | UUID | None): The user who created the patient."""

        if create:
            if extracted:
                last_history = self.history.order_by("history_date").first()
                user = (
                    extracted
                    if isinstance(extracted, User)
                    else User.objects.get(id=extracted)
                )
                last_history.history_user = user
                last_history.save()
