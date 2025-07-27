from collections.abc import Sequence
from typing import Any
from typing import Literal
from uuid import UUID

from factory import Faker
from factory import RelatedFactory
from factory import post_generation
from factory.django import DjangoModelFactory

from gouthelper_ninja.dateofbirths.tests.factories import DateOfBirthFactory
from gouthelper_ninja.ethnicitys.tests.factories import EthnicityFactory
from gouthelper_ninja.genders.tests.factories import GenderFactory
from gouthelper_ninja.goutdetails.tests.factories import GoutDetailFactory
from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.medhistorys.tests.factories import MedHistoryFactory
from gouthelper_ninja.profiles.helpers import get_provider_alias
from gouthelper_ninja.profiles.tests.factories import PatientProfileFactory
from gouthelper_ninja.users.models import User
from gouthelper_ninja.utils.helpers import age_calc


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
    dateofbirth = RelatedFactory(
        DateOfBirthFactory,
        factory_related_name="patient",
    )
    ethnicity = RelatedFactory(
        EthnicityFactory,
        factory_related_name="patient",
    )
    gender = RelatedFactory(
        GenderFactory,
        factory_related_name="patient",
    )
    gout = RelatedFactory(
        MedHistoryFactory,
        factory_related_name="patient",
        mhtype=MHTypes.GOUT,
        history_of=True,
    )
    goutdetail = RelatedFactory(
        GoutDetailFactory,
        factory_related_name="patient",
    )

    @post_generation
    def menopause(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False, "OMIT"] | None = True,  # noqa: FBT002
        **kwargs,
    ) -> None:
        """Post-generation hook to create a Menopause MedHistory for the patient.
        Because extracted will always be passed None in the absence of a value,
        we use "OMIT" to indicate that we do not want to create a Menopause
        MedHistory for the patient."""

        if create:
            if extracted != "OMIT":
                if extracted is not None:
                    kwargs["history_of"] = extracted
                MedHistoryFactory(
                    patient=self,
                    mhtype=MHTypes.MENOPAUSE,
                    **kwargs,
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

    @post_generation
    def angina(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.ANGINA,
                history_of=extracted,
            )

    @post_generation
    def anticoagulation(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.ANTICOAGULATION,
                history_of=extracted,
            )

    @post_generation
    def bleed(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.BLEED,
                history_of=extracted,
            )

    @post_generation
    def cad(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.CAD,
                history_of=extracted,
            )

    @post_generation
    def chf(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.CHF,
                history_of=extracted,
            )

    @post_generation
    def ckd(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.CKD,
                history_of=extracted,
            )

    @post_generation
    def colchicineinteraction(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.COLCHICINEINTERACTION,
                history_of=extracted,
            )

    @post_generation
    def diabetes(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        """Post-generation hook to create a Diabetes MedHistory for the patient.
        Defaults to creating a Diabetes MedHistory with history_of=True."""
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.DIABETES,
                history_of=extracted,  # True or False
            )

    @post_generation
    def erosions(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.EROSIONS,
                history_of=extracted,
            )

    @post_generation
    def gastricbypass(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.GASTRICBYPASS,
                history_of=extracted,
            )

    @post_generation
    def heartattack(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.HEARTATTACK,
                history_of=extracted,
            )

    @post_generation
    def hepatitis(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.HEPATITIS,
                history_of=extracted,
            )

    @post_generation
    def hypertension(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.HYPERTENSION,
                history_of=extracted,
            )

    @post_generation
    def hyperuricemia(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.HYPERURICEMIA,
                history_of=extracted,
            )

    @post_generation
    def ibd(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.IBD,
                history_of=extracted,
            )

    @post_generation
    def organtransplant(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.ORGANTRANSPLANT,
                history_of=extracted,
            )

    @post_generation
    def osteoporosis(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.OSTEOPOROSIS,
                history_of=extracted,
            )

    @post_generation
    def pad(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.PAD,
                history_of=extracted,
            )

    @post_generation
    def pud(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.PUD,
                history_of=extracted,
            )

    @post_generation
    def stroke(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.STROKE,
                history_of=extracted,
            )

    @post_generation
    def tophi(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.TOPHI,
                history_of=extracted,
            )

    @post_generation
    def uratestones(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.URATESTONES,
                history_of=extracted,
            )

    @post_generation
    def xoiinteraction(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None = True,  # noqa: FBT002
    ) -> None:
        if create and extracted is not None:
            MedHistoryFactory(
                patient=self,
                mhtype=MHTypes.XOIINTERACTION,
                history_of=extracted,
            )
