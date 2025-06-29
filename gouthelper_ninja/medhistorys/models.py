from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from gouthelper_ninja.medhistorys.choices import MedHistoryTypes
from gouthelper_ninja.medhistorys.helpers import medhistorys_get_default_medhistorytype
from gouthelper_ninja.medhistorys.managers import AnginaManager
from gouthelper_ninja.medhistorys.managers import AnticoagulationManager
from gouthelper_ninja.medhistorys.managers import BleedManager
from gouthelper_ninja.medhistorys.managers import CadManager
from gouthelper_ninja.medhistorys.managers import ChfManager
from gouthelper_ninja.medhistorys.managers import CkdManager
from gouthelper_ninja.medhistorys.managers import CkdRelationsManager
from gouthelper_ninja.medhistorys.managers import ColchicineinteractionManager
from gouthelper_ninja.medhistorys.managers import DiabetesManager
from gouthelper_ninja.medhistorys.managers import ErosionsManager
from gouthelper_ninja.medhistorys.managers import GastricbypassManager
from gouthelper_ninja.medhistorys.managers import GoutManager
from gouthelper_ninja.medhistorys.managers import GoutRelationsManager
from gouthelper_ninja.medhistorys.managers import HeartattackManager
from gouthelper_ninja.medhistorys.managers import HepatitisManager
from gouthelper_ninja.medhistorys.managers import HypertensionManager
from gouthelper_ninja.medhistorys.managers import HyperuricemiaManager
from gouthelper_ninja.medhistorys.managers import IbdManager
from gouthelper_ninja.medhistorys.managers import MenopauseManager
from gouthelper_ninja.medhistorys.managers import OrgantransplantManager
from gouthelper_ninja.medhistorys.managers import OsteoporosisManager
from gouthelper_ninja.medhistorys.managers import PudManager
from gouthelper_ninja.medhistorys.managers import PvdManager
from gouthelper_ninja.medhistorys.managers import StrokeManager
from gouthelper_ninja.medhistorys.managers import TophiManager
from gouthelper_ninja.medhistorys.managers import UratestonesManager
from gouthelper_ninja.medhistorys.managers import XoiinteractionManager
from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.rules import delete_object
from gouthelper_ninja.rules import view_object
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
            # Check that medhistorytype is in MedHistoryTypes.choices
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_medhistorytype_valid",
                check=models.Q(medhistorytype__in=MedHistoryTypes.values),
            ),
            # A Patient can only have one of each type of MedHistory
            models.UniqueConstraint(
                fields=["patient", "medhistorytype"],
                name="%(app_label)s_%(class)s_unique_patient",
            ),
        ]
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }

    MedHistoryTypes = MedHistoryTypes

    medhistorytype = models.CharField(
        _("MedHistory Type"),
        max_length=50,
        choices=MedHistoryTypes.choices,
        editable=False,
    )
    value = models.BooleanField(
        _("Value"),
        help_text="Does the patient have this medical history?",
        default=False,
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        editable=False,
    )
    history = HistoricalRecords()
    objects = models.Manager()

    def __str__(self):
        try:
            return f"{self.MedHistoryTypes(self.medhistorytype).label}"
        except ValueError:
            try:
                return f"{self.MedHistoryTypes(self._meta.model_name).label}"
            except ValueError:
                return f"{medhistorys_get_default_medhistorytype(self)} pre-save"

    def delete(
        self,
        *args,
        **kwargs,
    ):
        """Overwritten to change class before and after calling super().save()
        so Django-Simple-History works."""
        # Change class to MedHistory, call super().delete(), then change class back
        # to proxy model class in order for Django-Simple-History to work properly
        self.__class__ = MedHistory
        super().delete(*args, **kwargs)
        self.__class__ = apps.get_model(f"medhistorys.{self.medhistorytype}")

    def save(
        self,
        *args,
        **kwargs,
    ):
        """Overwritten to:
        1. Add medhistorytype on initial save.
        2. Change class before and after calling super().save()
        so Django-Simple-History works.
        """
        # Add medhistorytype on initial save
        if self._state.adding is True:
            if not self.medhistorytype:
                self.medhistorytype = medhistorys_get_default_medhistorytype(self)
        # Change class to MedHistory, call super().save(), then change class back
        # to proxy model class in order for Django-Simple-History to work properly
        self.__class__ = MedHistory
        super().save(*args, **kwargs)
        self.__class__ = apps.get_model(f"medhistorys.{self.medhistorytype}")


class Angina(MedHistory):
    """Model for history of cardiac chest pain."""

    class Meta:
        proxy = True

    objects = AnginaManager()


class Anticoagulation(MedHistory):
    """Model for Patient's anticoagulation use. HistoryDetail related object
    AnticoagulationDetail to describe which anticoagulants."""

    class Meta:
        proxy = True

    objects = AnticoagulationManager()


class Bleed(MedHistory):
    """Model for Patient's history of bleeding events."""

    class Meta:
        proxy = True

    objects = BleedManager()


class Cad(MedHistory):
    """Proxy model for Cad MedHistory objects."""

    class Meta:
        proxy = True

    objects = CadManager()


class Chf(MedHistory):
    """Describes whether Patient has a history of congestive heart failure."""

    class Meta:
        proxy = True

    objects = ChfManager()


class Ckd(MedHistory):
    """Whether Patient has a history of chronic kidney disease.
    Details are stored in HistoryDetail related object CkdDetail."""

    class Meta:
        proxy = True

    objects = CkdManager()
    related_objects = CkdRelationsManager()


class Colchicineinteraction(MedHistory):
    """Model for Patient being on a medication that interacts with colchicine.
    Details about which medication are stored in HistoryDetail related object
    ColchicineinteractionDetail."""

    class Meta:
        proxy = True

    objects = ColchicineinteractionManager()


class Diabetes(MedHistory):
    """Whether or not a Patient is diabetic."""

    class Meta:
        proxy = True

    objects = DiabetesManager()


class Erosions(MedHistory):
    """Whether or not a Patient has gouty erosions."""

    class Meta:
        proxy = True

    objects = ErosionsManager()


class Gastricbypass(MedHistory):
    """Whether or not a Patient has had gastric bypass surgery."""

    class Meta:
        proxy = True

    objects = GastricbypassManager()


class Gout(MedHistory):
    """Whether or not a Patient has gout. GoutDetail related object to describe
    whether or not a Patient is actively flaring or hyperuricemic (past 6 months)."""

    class Meta:
        proxy = True

    objects = GoutManager()
    related_objects = GoutRelationsManager()


class Heartattack(MedHistory):
    """Whether or not a Patient has had a heart attack."""

    class Meta:
        proxy = True

    objects = HeartattackManager()


class Hepatitis(MedHistory):
    """Whether or not a Patient has hepatitis or cirrhosis of the lvier."""

    class Meta:
        proxy = True

    objects = HepatitisManager()


class Hypertension(MedHistory):
    """Stores whether or not a Patient has a history of hypertension."""

    class Meta:
        proxy = True

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

    class Meta:
        proxy = True

    objects = HyperuricemiaManager()


class Ibd(MedHistory):
    """Records history of a Patient's inflammatory bowel disease."""

    class Meta:
        proxy = True

    objects = IbdManager()


class Menopause(MedHistory):
    """Records medical history of menopause. Mostly for figuring out if a
    woman who is having symptoms could be having a gout flare."""

    class Meta:
        proxy = True

    objects = MenopauseManager()


class Organtransplant(MedHistory):
    """Records medical history of an organ transplant. Related
    object OrgantransplantDetail stores details of the transplant."""

    class Meta:
        proxy = True

    objects = OrgantransplantManager()


class Osteoporosis(MedHistory):
    """Records medical history of osteoporosis."""

    class Meta:
        proxy = True

    objects = OsteoporosisManager()


class Pud(MedHistory):
    """Records medical history of peptic ulcer disease."""

    class Meta:
        proxy = True

    objects = PudManager()


class Pvd(MedHistory):
    """Records medical history of peripheral vascular disease."""

    class Meta:
        proxy = True

    objects = PvdManager()


class Stroke(MedHistory):
    """Patient's history of stroke."""

    class Meta:
        proxy = True

    objects = StrokeManager()


class Tophi(MedHistory):
    """Patient's history of gouty tophi."""

    class Meta:
        proxy = True

    objects = TophiManager()


class Uratestones(MedHistory):
    """Patient's history of urate kidney stones."""

    class Meta:
        proxy = True

    objects = UratestonesManager()


class Xoiinteraction(MedHistory):
    class Meta:
        proxy = True

    objects = XoiinteractionManager()
