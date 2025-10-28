from collections.abc import Sequence
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import Union
from uuid import UUID

from factory import Faker
from factory import RelatedFactory
from factory import post_generation
from factory.base import StubObject
from factory.django import DjangoModelFactory

from gouthelper_ninja.ckddetails.tests.factories import CkdDetailFactory
from gouthelper_ninja.dateofbirths.tests.factories import DateOfBirthFactory
from gouthelper_ninja.ethnicitys.tests.factories import EthnicityFactory
from gouthelper_ninja.genders.tests.factories import GenderFactory
from gouthelper_ninja.goutdetails.tests.factories import GoutDetailFactory
from gouthelper_ninja.labs.helpers import BaselineCreatinineCalc
from gouthelper_ninja.labs.tests.factories import BaselineCreatinineFactory
from gouthelper_ninja.medhistorys.helpers import menopause_required
from gouthelper_ninja.medhistorys.tests.factories import AnginaFactory
from gouthelper_ninja.medhistorys.tests.factories import AnticoagulationFactory
from gouthelper_ninja.medhistorys.tests.factories import BleedFactory
from gouthelper_ninja.medhistorys.tests.factories import CadFactory
from gouthelper_ninja.medhistorys.tests.factories import ChfFactory
from gouthelper_ninja.medhistorys.tests.factories import CkdFactory
from gouthelper_ninja.medhistorys.tests.factories import ColchicineinteractionFactory
from gouthelper_ninja.medhistorys.tests.factories import DiabetesFactory
from gouthelper_ninja.medhistorys.tests.factories import ErosionsFactory
from gouthelper_ninja.medhistorys.tests.factories import GastricbypassFactory
from gouthelper_ninja.medhistorys.tests.factories import GoutFactory
from gouthelper_ninja.medhistorys.tests.factories import HeartattackFactory
from gouthelper_ninja.medhistorys.tests.factories import HepatitisFactory
from gouthelper_ninja.medhistorys.tests.factories import HypertensionFactory
from gouthelper_ninja.medhistorys.tests.factories import HyperuricemiaFactory
from gouthelper_ninja.medhistorys.tests.factories import IbdFactory
from gouthelper_ninja.medhistorys.tests.factories import MenopauseFactory
from gouthelper_ninja.medhistorys.tests.factories import OrgantransplantFactory
from gouthelper_ninja.medhistorys.tests.factories import OsteoporosisFactory
from gouthelper_ninja.medhistorys.tests.factories import PadFactory
from gouthelper_ninja.medhistorys.tests.factories import PudFactory
from gouthelper_ninja.medhistorys.tests.factories import StrokeFactory
from gouthelper_ninja.medhistorys.tests.factories import TophiFactory
from gouthelper_ninja.medhistorys.tests.factories import UratestonesFactory
from gouthelper_ninja.medhistorys.tests.factories import XoiinteractionFactory
from gouthelper_ninja.profiles.tests.factories import PatientProfileFactory
from gouthelper_ninja.ults.tests.factories import UltFactory
from gouthelper_ninja.users.models import User
from gouthelper_ninja.utils.helpers import age_calc

if TYPE_CHECKING:
    from decimal import Decimal


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
        # Set the password only if the instance is not a StubObject,
        # as a StubObject does not have the set_password method.
        # This is to avoid errors when using PatientFactory as a
        # SubFactory in other factories.
        if not isinstance(self, StubObject):
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
        GoutFactory,
        factory_related_name="patient",
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
        extracted: Literal[True, False, "OMIT"] | None,
        **kwargs,
    ) -> None:
        """Post-generation hook to create a Menopause MedHistory for the patient.
        Because extracted will always be passed None in the absence of a value,
        we use "OMIT" to indicate that we do not want to create a Menopause
        MedHistory for the patient."""

        if create:
            if extracted != "OMIT" and (
                extracted is not None
                or (
                    hasattr(self, "dateofbirth")
                    and hasattr(self, "gender")
                    and menopause_required(
                        gender=self.gender.gender,
                        age=age_calc(self.dateofbirth.dateofbirth),
                    )
                )
            ):
                if extracted is not None:
                    kwargs["history_of"] = extracted
                MenopauseFactory(
                    patient=self,
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
            PatientProfileFactory(patient=self, **kwargs)

    @post_generation
    def creator(
        self,
        create: Literal[True, False],
        extracted: User | UUID | None,
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
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            AnginaFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def anticoagulation(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            AnticoagulationFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def bleed(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            BleedFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def cad(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            CadFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def chf(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            ChfFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def ckd(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            CkdFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def ckddetail(
        self,
        create: Literal[True, False],
        # ckddetail argument can either be a dict of CkdDetail field values
        # or True, indicating that a CkdDetail should be created
        # without specific field values
        extracted: dict[str, Any] | Literal[True] | None,
    ) -> None:
        if create and extracted is not None:
            # If a CkdDetail is being created, the Patient
            # should have CKD
            if not hasattr(self, "ckd"):
                CkdFactory(
                    patient=self,
                    history_of=True,
                )
            kwargs = {}
            # If ckddetail arg is a dictionary of field values
            # it should be unpacked into the CkdDetailFactory
            if isinstance(extracted, dict):
                kwargs = extracted
            CkdDetailFactory(
                patient=self,
                **kwargs,
            )

    @post_generation
    def baselinecreatinine(
        self,
        create: Literal[True, False],
        # baselinecreatinine argument can either be a Decimal value
        # or True, indicating that a BaselineCreatinine should be created
        # without specific field values
        extracted: Union["Decimal", Literal[True], None],
    ) -> None:
        if create and extracted is not None:
            # If a BaselineCreatinine is being created, the Patient
            # should have CKD
            if self.ckd is None:
                CkdFactory(
                    patient=self,
                    history_of=True,
                )
            kwargs = {}
            if extracted is True:
                if hasattr(self, "ckddetail"):
                    # Calculate range of creatinine values compatible with
                    # the CKD stage
                    kwargs.update(
                        {
                            "value": BaselineCreatinineCalc(
                                stage=self.ckddetail.stage,
                                age=self.age,
                                gender=self.gender,
                            ).calculate(),
                        },
                    )
            else:
                kwargs.update(
                    {"value": extracted},
                )
            BaselineCreatinineFactory(
                patient=self,
                **kwargs,
            )

    @post_generation
    def colchicineinteraction(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            ColchicineinteractionFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def diabetes(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        """Post-generation hook to create a Diabetes MedHistory for the patient.
        Defaults to creating a Diabetes MedHistory with history_of=True."""
        if create and extracted is not None:
            DiabetesFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def erosions(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            ErosionsFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def gastricbypass(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            GastricbypassFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def heartattack(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            HeartattackFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def hepatitis(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            HepatitisFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def hypertension(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            HypertensionFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def hyperuricemia(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            HyperuricemiaFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def ibd(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            IbdFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def organtransplant(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            OrgantransplantFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def osteoporosis(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            OsteoporosisFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def pad(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            PadFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def pud(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            PudFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def stroke(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            StrokeFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def tophi(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            TophiFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def ult(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            UltFactory(patient=self)

    @post_generation
    def uratestones(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            UratestonesFactory(
                patient=self,
                history_of=extracted,
            )

    @post_generation
    def xoiinteraction(
        self,
        create: Literal[True, False],
        extracted: Literal[True, False] | None,
    ) -> None:
        if create and extracted is not None:
            XoiinteractionFactory(
                patient=self,
                history_of=extracted,
            )
