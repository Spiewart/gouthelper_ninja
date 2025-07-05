import pytest

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
from gouthelper_ninja.medhistorys.models import Menopause
from gouthelper_ninja.medhistorys.models import Organtransplant
from gouthelper_ninja.medhistorys.models import Osteoporosis
from gouthelper_ninja.medhistorys.models import Pad
from gouthelper_ninja.medhistorys.models import Stroke
from gouthelper_ninja.medhistorys.models import Tophi
from gouthelper_ninja.medhistorys.models import Uratestones
from gouthelper_ninja.medhistorys.models import Xoiinteraction
from gouthelper_ninja.medhistorys.schema import MedHistoryEditSchema
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
from gouthelper_ninja.medhistorys.tests.factories import StrokeFactory
from gouthelper_ninja.medhistorys.tests.factories import TophiFactory
from gouthelper_ninja.medhistorys.tests.factories import UratestonesFactory
from gouthelper_ninja.medhistorys.tests.factories import XoiinteractionFactory
from gouthelper_ninja.users.tests.factories import PatientFactory


def make_schema(history_of=True):  # noqa: FBT002
    return MedHistoryEditSchema(history_of=history_of)


@pytest.mark.django_db
def test_angina_manager_queryset_and_gh_create():
    obj = AnginaFactory()
    assert Angina.objects.filter(pk=obj.pk).exists()
    assert obj.mhtype == MHTypes.ANGINA
    # Test create method
    patient = PatientFactory()
    schema = make_schema()
    created = Angina.objects.gh_create(data=schema, patient_id=patient.id)
    assert created.mhtype == MHTypes.ANGINA
    assert Angina.objects.filter(pk=created.pk).exists()


@pytest.mark.django_db
def test_anticoagulation_manager_queryset_and_gh_create():
    obj = AnticoagulationFactory()
    assert Anticoagulation.objects.filter(pk=obj.pk).exists()
    assert obj.mhtype == MHTypes.ANTICOAGULATION
    patient = PatientFactory()
    schema = make_schema()
    created = Anticoagulation.objects.gh_create(data=schema, patient_id=patient.id)
    assert created.mhtype == MHTypes.ANTICOAGULATION
    assert Anticoagulation.objects.filter(pk=created.pk).exists()


@pytest.mark.django_db
def test_bleed_manager_queryset_and_gh_create():
    obj = BleedFactory()
    assert Bleed.objects.filter(pk=obj.pk).exists()
    assert obj.mhtype == MHTypes.BLEED
    patient = PatientFactory()
    schema = make_schema()
    created = Bleed.objects.gh_create(data=schema, patient_id=patient.id)
    assert created.mhtype == MHTypes.BLEED
    assert Bleed.objects.filter(pk=created.pk).exists()


@pytest.mark.parametrize(
    ("model", "factory", "mhtype"),
    [
        (Cad, CadFactory, MHTypes.CAD),
        (Chf, ChfFactory, MHTypes.CHF),
        (Ckd, CkdFactory, MHTypes.CKD),
        (
            Colchicineinteraction,
            ColchicineinteractionFactory,
            MHTypes.COLCHICINEINTERACTION,
        ),
        (Diabetes, DiabetesFactory, MHTypes.DIABETES),
        (Erosions, ErosionsFactory, MHTypes.EROSIONS),
        (Gastricbypass, GastricbypassFactory, MHTypes.GASTRICBYPASS),
        (Gout, GoutFactory, MHTypes.GOUT),
        (Heartattack, HeartattackFactory, MHTypes.HEARTATTACK),
        (Hepatitis, HepatitisFactory, MHTypes.HEPATITIS),
        (Hypertension, HypertensionFactory, MHTypes.HYPERTENSION),
        (Hyperuricemia, HyperuricemiaFactory, MHTypes.HYPERURICEMIA),
        (Ibd, IbdFactory, MHTypes.IBD),
        (Menopause, MenopauseFactory, MHTypes.MENOPAUSE),
        (Organtransplant, OrgantransplantFactory, MHTypes.ORGANTRANSPLANT),
        (Osteoporosis, OsteoporosisFactory, MHTypes.OSTEOPOROSIS),
        (Pad, PadFactory, MHTypes.PAD),
        (Stroke, StrokeFactory, MHTypes.STROKE),
        (Tophi, TophiFactory, MHTypes.TOPHI),
        (Uratestones, UratestonesFactory, MHTypes.URATESTONES),
        (Xoiinteraction, XoiinteractionFactory, MHTypes.XOIINTERACTION),
    ],
)
@pytest.mark.django_db
def test_manager_queryset_and_gh_create(model, factory, mhtype):
    obj = factory()
    assert model.objects.filter(pk=obj.pk).exists()
    assert obj.mhtype == mhtype
    patient = PatientFactory()
    schema = make_schema()
    created = model.objects.gh_create(data=schema, patient_id=patient.id)
    assert created.mhtype == mhtype
    assert model.objects.filter(pk=created.pk).exists()
