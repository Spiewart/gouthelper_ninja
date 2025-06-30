import pytest

from gouthelper_ninja.medhistorys.choices import MedHistoryTypes
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
from gouthelper_ninja.medhistorys.models import Menopause
from gouthelper_ninja.medhistorys.models import Organtransplant
from gouthelper_ninja.medhistorys.models import Osteoporosis
from gouthelper_ninja.medhistorys.models import Pvd
from gouthelper_ninja.medhistorys.models import Stroke
from gouthelper_ninja.medhistorys.models import Tophi
from gouthelper_ninja.medhistorys.models import Uratestones
from gouthelper_ninja.medhistorys.models import Xoiinteraction
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
from gouthelper_ninja.medhistorys.tests.factories import PvdFactory
from gouthelper_ninja.medhistorys.tests.factories import StrokeFactory
from gouthelper_ninja.medhistorys.tests.factories import TophiFactory
from gouthelper_ninja.medhistorys.tests.factories import UratestonesFactory
from gouthelper_ninja.medhistorys.tests.factories import XoiinteractionFactory
from gouthelper_ninja.users.tests.factories import PatientFactory


@pytest.mark.django_db
def test_angina_manager_queryset_and_create():
    obj = AnginaFactory()
    assert Angina.objects.filter(pk=obj.pk).exists()
    assert obj.medhistorytype == MedHistoryTypes.ANGINA
    # Test create method
    created = Angina.objects.create(patient=PatientFactory(), history_of=True)
    assert created.medhistorytype == MedHistoryTypes.ANGINA
    assert Angina.objects.filter(pk=created.pk).exists()


@pytest.mark.django_db
def test_anticoagulation_manager_queryset_and_create():
    obj = AnticoagulationFactory()
    assert Anticoagulation.objects.filter(pk=obj.pk).exists()
    assert obj.medhistorytype == MedHistoryTypes.ANTICOAGULATION
    created = Anticoagulation.objects.create(patient=PatientFactory(), history_of=True)
    assert created.medhistorytype == MedHistoryTypes.ANTICOAGULATION
    assert Anticoagulation.objects.filter(pk=created.pk).exists()


@pytest.mark.django_db
def test_bleed_manager_queryset_and_create():
    obj = BleedFactory()
    assert Bleed.objects.filter(pk=obj.pk).exists()
    assert obj.medhistorytype == MedHistoryTypes.BLEED
    created = Bleed.objects.create(patient=PatientFactory(), history_of=True)
    assert created.medhistorytype == MedHistoryTypes.BLEED
    assert Bleed.objects.filter(pk=created.pk).exists()


# ...repeat for all other managers...


@pytest.mark.parametrize(
    ("model", "factory", "medhistorytype"),
    [
        (Cad, CadFactory, MedHistoryTypes.CAD),
        (Chf, ChfFactory, MedHistoryTypes.CHF),
        (Ckd, CkdFactory, MedHistoryTypes.CKD),
        (
            Colchicineinteraction,
            ColchicineinteractionFactory,
            MedHistoryTypes.COLCHICINEINTERACTION,
        ),
        (Diabetes, DiabetesFactory, MedHistoryTypes.DIABETES),
        (Erosions, ErosionsFactory, MedHistoryTypes.EROSIONS),
        (Gastricbypass, GastricbypassFactory, MedHistoryTypes.GASTRICBYPASS),
        (Gout, GoutFactory, MedHistoryTypes.GOUT),
        (Heartattack, HeartattackFactory, MedHistoryTypes.HEARTATTACK),
        (Hepatitis, HepatitisFactory, MedHistoryTypes.HEPATITIS),
        (Hypertension, HypertensionFactory, MedHistoryTypes.HYPERTENSION),
        (Hyperuricemia, HyperuricemiaFactory, MedHistoryTypes.HYPERURICEMIA),
        (Ibd, IbdFactory, MedHistoryTypes.IBD),
        (Menopause, MenopauseFactory, MedHistoryTypes.MENOPAUSE),
        (Organtransplant, OrgantransplantFactory, MedHistoryTypes.ORGANTRANSPLANT),
        (Osteoporosis, OsteoporosisFactory, MedHistoryTypes.OSTEOPOROSIS),
        (Pvd, PvdFactory, MedHistoryTypes.PVD),
        (Stroke, StrokeFactory, MedHistoryTypes.STROKE),
        (Tophi, TophiFactory, MedHistoryTypes.TOPHI),
        (Uratestones, UratestonesFactory, MedHistoryTypes.URATESTONES),
        (Xoiinteraction, XoiinteractionFactory, MedHistoryTypes.XOIINTERACTION),
    ],
)
@pytest.mark.django_db
def test_manager_queryset_and_create(model, factory, medhistorytype):
    obj = factory()
    assert model.objects.filter(pk=obj.pk).exists()
    assert obj.medhistorytype == medhistorytype
    created = model.objects.create(history_of=True, patient=PatientFactory())
    assert created.medhistorytype == medhistorytype
    assert model.objects.filter(pk=created.pk).exists()
