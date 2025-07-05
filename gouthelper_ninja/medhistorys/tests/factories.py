from factory import SubFactory
from factory import fuzzy
from factory.django import DjangoModelFactory
from factory.faker import faker

from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.medhistorys.models import Angina
from gouthelper_ninja.medhistorys.models import Anticoagulation
from gouthelper_ninja.medhistorys.models import Bleed
from gouthelper_ninja.medhistorys.models import Cad
from gouthelper_ninja.medhistorys.models import Chf
from gouthelper_ninja.medhistorys.models import Ckd
from gouthelper_ninja.medhistorys.models import Colchicineinteraction
from gouthelper_ninja.medhistorys.models import Diabetes
from gouthelper_ninja.medhistorys.models import Erosions
from gouthelper_ninja.medhistorys.models import Gastricbypass
from gouthelper_ninja.medhistorys.models import Gout
from gouthelper_ninja.medhistorys.models import Heartattack
from gouthelper_ninja.medhistorys.models import Hepatitis
from gouthelper_ninja.medhistorys.models import Hypertension
from gouthelper_ninja.medhistorys.models import Hyperuricemia
from gouthelper_ninja.medhistorys.models import Ibd
from gouthelper_ninja.medhistorys.models import MedHistory
from gouthelper_ninja.medhistorys.models import Menopause
from gouthelper_ninja.medhistorys.models import Organtransplant
from gouthelper_ninja.medhistorys.models import Osteoporosis
from gouthelper_ninja.medhistorys.models import Pad
from gouthelper_ninja.medhistorys.models import Pud
from gouthelper_ninja.medhistorys.models import Stroke
from gouthelper_ninja.medhistorys.models import Tophi
from gouthelper_ninja.medhistorys.models import Uratestones
from gouthelper_ninja.medhistorys.models import Xoiinteraction

fake = faker.Faker()


class MedHistoryFactory(DjangoModelFactory):
    class Meta:
        model = MedHistory

    mhtype = fuzzy.FuzzyChoice(MHTypes.values)
    history_of = fake.boolean()
    patient = SubFactory("gouthelper_ninja.users.tests.factories.PatientFactory")


class AnginaFactory(MedHistoryFactory):
    class Meta:
        model = Angina


class AnticoagulationFactory(MedHistoryFactory):
    class Meta:
        model = Anticoagulation


class BleedFactory(MedHistoryFactory):
    class Meta:
        model = Bleed


class CadFactory(MedHistoryFactory):
    class Meta:
        model = Cad


class ChfFactory(MedHistoryFactory):
    class Meta:
        model = Chf


class CkdFactory(MedHistoryFactory):
    class Meta:
        model = Ckd


class ColchicineinteractionFactory(MedHistoryFactory):
    class Meta:
        model = Colchicineinteraction


class DiabetesFactory(MedHistoryFactory):
    class Meta:
        model = Diabetes


class ErosionsFactory(MedHistoryFactory):
    class Meta:
        model = Erosions


class GastricbypassFactory(MedHistoryFactory):
    class Meta:
        model = Gastricbypass


class GoutFactory(MedHistoryFactory):
    class Meta:
        model = Gout


class HeartattackFactory(MedHistoryFactory):
    class Meta:
        model = Heartattack


class HepatitisFactory(MedHistoryFactory):
    class Meta:
        model = Hepatitis


class HypertensionFactory(MedHistoryFactory):
    class Meta:
        model = Hypertension


class HyperuricemiaFactory(MedHistoryFactory):
    class Meta:
        model = Hyperuricemia


class IbdFactory(MedHistoryFactory):
    class Meta:
        model = Ibd


class MenopauseFactory(MedHistoryFactory):
    class Meta:
        model = Menopause


class OrgantransplantFactory(MedHistoryFactory):
    class Meta:
        model = Organtransplant


class OsteoporosisFactory(MedHistoryFactory):
    class Meta:
        model = Osteoporosis


class PadFactory(MedHistoryFactory):
    class Meta:
        model = Pad


class StrokeFactory(MedHistoryFactory):
    class Meta:
        model = Stroke


class TophiFactory(MedHistoryFactory):
    class Meta:
        model = Tophi


class UratestonesFactory(MedHistoryFactory):
    class Meta:
        model = Uratestones


class XoiinteractionFactory(MedHistoryFactory):
    class Meta:
        model = Xoiinteraction


class PudFactory(MedHistoryFactory):
    class Meta:
        model = Pud
