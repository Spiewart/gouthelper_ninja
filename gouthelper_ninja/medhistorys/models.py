from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from gouthelper_ninja.medhistorys.schema import MedHistoryEditSchema
from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.rules import delete_object
from gouthelper_ninja.rules import view_object
from gouthelper_ninja.utils.models import PatientOneToOne


class MedHistory(
    PatientOneToOne,
    TimeStampedModel,
):
    """GoutHelper MedHistory model to store medical, family, social history data
    for Patients. value field is a Boolean that is required and defaults to False.
    """

    class Meta(PatientOneToOne.Meta):
        abstract = True

    history_of = models.BooleanField(
        _("History of"),
        help_text="Does the patient have this medical history?",
        default=False,
    )
    edit_schema = MedHistoryEditSchema
    history = HistoricalRecords(inherit=True)

    def __str__(self):
        """Returns a string representation of the MedHistory object."""
        return f"{self.patient} - {self.__class__.__name__.lower()}: {self.history_of}"

    def get_absolute_url(self):
        return reverse("users:patient-detail", kwargs={"patient": self.patient.id})


class Angina(MedHistory):
    """Model for history of cardiac chest pain."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Anticoagulation(MedHistory):
    """Model for Patient's anticoagulation use. HistoryDetail related object
    AnticoagulationDetail to describe which anticoagulants."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Bleed(MedHistory):
    """Model for Patient's history of bleeding events."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Cad(MedHistory):
    """Proxy model for Cad MedHistory objects."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Chf(MedHistory):
    """Describes whether Patient has a history of congestive heart failure."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Ckd(MedHistory):
    """Whether Patient has a history of chronic kidney disease."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Colchicineinteraction(MedHistory):
    """Model for Patient being on a medication that interacts with colchicine.
    Details about which medication are stored in HistoryDetail related object
    ColchicineinteractionDetail."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Diabetes(MedHistory):
    """Whether or not a Patient is diabetic."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Erosions(MedHistory):
    """Whether or not a Patient has gouty erosions."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Gastricbypass(MedHistory):
    """Whether or not a Patient has had gastric bypass surgery."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Gout(MedHistory):
    """Whether or not a Patient has gout."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Heartattack(MedHistory):
    """Whether or not a Patient has had a heart attack."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Hepatitis(MedHistory):
    """Whether or not a Patient has hepatitis or cirrhosis of the lvier."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Hypertension(MedHistory):
    """Stores whether or not a Patient has a history of hypertension."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


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

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Ibd(MedHistory):
    """Records history of a Patient's inflammatory bowel disease."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Menopause(MedHistory):
    """Records medical history of menopause. Mostly for figuring out if a
    woman who is having symptoms could be having a gout flare."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Organtransplant(MedHistory):
    """Records medical history of an organ transplant. Related
    object OrgantransplantDetail stores details of the transplant."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Osteoporosis(MedHistory):
    """Records medical history of osteoporosis."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Pud(MedHistory):
    """Records medical history of peptic ulcer disease."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Pad(MedHistory):
    """Records medical history of peripheral vascular disease."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Stroke(MedHistory):
    """Patient's history of stroke."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Tophi(MedHistory):
    """Patient's history of gouty tophi."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Uratestones(MedHistory):
    """Patient's history of urate kidney stones."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }


class Xoiinteraction(MedHistory):
    """Model for Patient being on a medication that interacts with xanthine
    oxidase inhibitors. These are chiefly azathioprine and mercaptopurine,
    but historically theophylline was also included."""

    class Meta(PatientOneToOne.Meta):
        rules_permissions = {
            "add": add_object,
            "change": change_object,
            "delete": delete_object,
            "view": view_object,
        }
