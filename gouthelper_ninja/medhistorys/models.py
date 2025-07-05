from django.apps import apps
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.medhistorys.managers import AnginaManager
from gouthelper_ninja.medhistorys.managers import AnticoagulationManager
from gouthelper_ninja.medhistorys.managers import BleedManager
from gouthelper_ninja.medhistorys.managers import CadManager
from gouthelper_ninja.medhistorys.managers import ChfManager
from gouthelper_ninja.medhistorys.managers import CkdManager
from gouthelper_ninja.medhistorys.managers import ColchicineinteractionManager
from gouthelper_ninja.medhistorys.managers import DiabetesManager
from gouthelper_ninja.medhistorys.managers import ErosionsManager
from gouthelper_ninja.medhistorys.managers import GastricbypassManager
from gouthelper_ninja.medhistorys.managers import GoutManager
from gouthelper_ninja.medhistorys.managers import HeartattackManager
from gouthelper_ninja.medhistorys.managers import HepatitisManager
from gouthelper_ninja.medhistorys.managers import HypertensionManager
from gouthelper_ninja.medhistorys.managers import HyperuricemiaManager
from gouthelper_ninja.medhistorys.managers import IbdManager
from gouthelper_ninja.medhistorys.managers import MenopauseManager
from gouthelper_ninja.medhistorys.managers import OrgantransplantManager
from gouthelper_ninja.medhistorys.managers import OsteoporosisManager
from gouthelper_ninja.medhistorys.managers import PadManager
from gouthelper_ninja.medhistorys.managers import PudManager
from gouthelper_ninja.medhistorys.managers import StrokeManager
from gouthelper_ninja.medhistorys.managers import TophiManager
from gouthelper_ninja.medhistorys.managers import UratestonesManager
from gouthelper_ninja.medhistorys.managers import XoiinteractionManager
from gouthelper_ninja.medhistorys.schema import MedHistoryEditSchema
from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.rules import delete_object
from gouthelper_ninja.rules import view_object
from gouthelper_ninja.utils.helpers import get_user_change
from gouthelper_ninja.utils.models import GoutHelperModel


class MedHistory(
    GoutHelperModel,
    TimeStampedModel,
):
    """GoutHelper MedHistory model to store medical, family, social history data
    for Patients. value field is a Boolean that is required and defaults to False.
    """

    class Meta(GoutHelperModel.Meta):
        constraints = [
            # Check that mhtype is in MHTypes.choices
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_mhtype_valid",
                condition=models.Q(mhtype__in=MHTypes.values),
            ),
            # A Patient can only have one of each type of MedHistory
            models.UniqueConstraint(
                fields=["patient", "mhtype"],
                name="%(app_label)s_%(class)s_unique_patient",
            ),
        ]
        # rules_permissions is NOT heritable, must be defined in child classes
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    MHTypes = MHTypes

    mhtype = models.CharField(
        _("Type of medical history"),
        max_length=50,
        choices=MHTypes.choices,
        editable=False,
    )
    history_of = models.BooleanField(
        _("History of"),
        help_text="Does the patient have this medical history?",
        default=False,
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        editable=False,
    )
    history = HistoricalRecords(get_user=get_user_change)
    objects = models.Manager()

    edit_schema = MedHistoryEditSchema

    def __str__(self):
        """Returns a string representation of the MedHistory object."""
        return f"{self.patient} - {self.get_mhtype_display()}: {self.history_of}"

    def delete(
        self,
        *args,
        **kwargs,
    ):
        """Overwritten to change class before and after calling super().save()
        so Django-Simple-History updates the HistoricalMedHistory table."""
        self.__class__ = MedHistory
        super().delete(*args, **kwargs)
        self.__class__ = apps.get_model(f"medhistorys.{self.mhtype}")

    def get_absolute_url(self):
        return reverse("users:patient-detail", kwargs={"patient": self.patient.id})

    def save(
        self,
        *args,
        **kwargs,
    ):
        """Overwritten to change class before and after calling super().save()
        so Django-Simple-History updates the HistoricalMedHistory table."""
        self.__class__ = MedHistory
        super().save(*args, **kwargs)
        self.__class__ = apps.get_model(f"medhistorys.{self.mhtype}")


class Angina(MedHistory):
    """Model for history of cardiac chest pain."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = AnginaManager()


class Anticoagulation(MedHistory):
    """Model for Patient's anticoagulation use. HistoryDetail related object
    AnticoagulationDetail to describe which anticoagulants."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = AnticoagulationManager()


class Bleed(MedHistory):
    """Model for Patient's history of bleeding events."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = BleedManager()


class Cad(MedHistory):
    """Proxy model for Cad MedHistory objects."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = CadManager()


class Chf(MedHistory):
    """Describes whether Patient has a history of congestive heart failure."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = ChfManager()


class Ckd(MedHistory):
    """Whether Patient has a history of chronic kidney disease."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = CkdManager()


class Colchicineinteraction(MedHistory):
    """Model for Patient being on a medication that interacts with colchicine.
    Details about which medication are stored in HistoryDetail related object
    ColchicineinteractionDetail."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = ColchicineinteractionManager()


class Diabetes(MedHistory):
    """Whether or not a Patient is diabetic."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = DiabetesManager()


class Erosions(MedHistory):
    """Whether or not a Patient has gouty erosions."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = ErosionsManager()


class Gastricbypass(MedHistory):
    """Whether or not a Patient has had gastric bypass surgery."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = GastricbypassManager()


class Gout(MedHistory):
    """Whether or not a Patient has gout."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = GoutManager()


class Heartattack(MedHistory):
    """Whether or not a Patient has had a heart attack."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = HeartattackManager()


class Hepatitis(MedHistory):
    """Whether or not a Patient has hepatitis or cirrhosis of the lvier."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = HepatitisManager()


class Hypertension(MedHistory):
    """Stores whether or not a Patient has a history of hypertension."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = HypertensionManager()


class Hyperuricemia(MedHistory):
    """MedHistory class to indicate whether a Patient has EVER had hyperuricemia
    defined as a serum uric acid > 9 mg/dL.

    This is based off the 2020 ACR guidelines where CKD stage >=3 and serum uric acid
    > 9 mg/dL is a low-evidence, conditional recommendation for ULT.

    FitzGerald JD, Dalbeth N, Mikuls T, Brignardello-Petersen R, Guyatt G, Abeles AM,
    Gelber AC, Harrold LR, Khanna D, King C, Levy G, Libbey C, Mount D, Pillinger MH,
    Rosenthal A, Singh JA, Sims JE, Smith BJ, Wenger NS, Bae SS, Danve A, Khanna PP,
    Kim SC, Lenert A, Poon S, Qasim A, Sehra ST, Sharma TSK, Toprover M, Turgunbaev M,
    Zeng L, Zhang MA, Turner AS, Neogi T.
    2020 American College of Rheumatology Guideline for the Management of Gout.
    Arthritis Care Res (Hoboken).
    2020 Jun;72(6):744-760. doi: 10.1002/acr.24180. Epub 2020 May 11. Erratum in:
    Arthritis Care Res (Hoboken).
    2020 Aug;72(8):1187. Erratum in: Arthritis Care Res (Hoboken). 2021 Mar;73(3):458.
    PMID: 32391934.
    """

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = HyperuricemiaManager()


class Ibd(MedHistory):
    """Records history of a Patient's inflammatory bowel disease."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = IbdManager()


class Menopause(MedHistory):
    """Records medical history of menopause. Mostly for figuring out if a
    woman who is having symptoms could be having a gout flare."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = MenopauseManager()


class Organtransplant(MedHistory):
    """Records medical history of an organ transplant. Related
    object OrgantransplantDetail stores details of the transplant."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = OrgantransplantManager()


class Osteoporosis(MedHistory):
    """Records medical history of osteoporosis."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = OsteoporosisManager()


class Pud(MedHistory):
    """Records medical history of peptic ulcer disease."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = PudManager()


class Pad(MedHistory):
    """Records medical history of peripheral vascular disease."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = PadManager()


class Stroke(MedHistory):
    """Patient's history of stroke."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = StrokeManager()


class Tophi(MedHistory):
    """Patient's history of gouty tophi."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = TophiManager()


class Uratestones(MedHistory):
    """Patient's history of urate kidney stones."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = UratestonesManager()


class Xoiinteraction(MedHistory):
    """Model for Patient being on a medication that interacts with xanthine
    oxidase inhibitors. These are chiefly azathioprine and mercaptopurine,
    but historically theophylline was also included."""

    class Meta(GoutHelperModel.Meta):
        proxy = True
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    objects = XoiinteractionManager()
