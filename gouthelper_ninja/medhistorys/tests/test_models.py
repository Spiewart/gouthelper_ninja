import pytest
from django.db import IntegrityError

from gouthelper_ninja.medhistorys.models import MedHistory
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
from gouthelper_ninja.medhistorys.tests.factories import MedHistoryFactory
from gouthelper_ninja.medhistorys.tests.factories import MenopauseFactory
from gouthelper_ninja.medhistorys.tests.factories import OrgantransplantFactory
from gouthelper_ninja.medhistorys.tests.factories import OsteoporosisFactory
from gouthelper_ninja.medhistorys.tests.factories import PadFactory
from gouthelper_ninja.medhistorys.tests.factories import PudFactory
from gouthelper_ninja.medhistorys.tests.factories import StrokeFactory
from gouthelper_ninja.medhistorys.tests.factories import TophiFactory
from gouthelper_ninja.medhistorys.tests.factories import UratestonesFactory
from gouthelper_ninja.medhistorys.tests.factories import XoiinteractionFactory
from gouthelper_ninja.users.tests.factories import PatientFactory


@pytest.mark.django_db
def test_medhistory_str():
    obj = MedHistoryFactory()
    s = str(obj)
    assert obj.patient.username in s
    assert str(obj.get_mhtype_display()) in s
    assert str(obj.history_of) in s


@pytest.mark.django_db
def test_unique_constraint():
    obj = MedHistoryFactory(
        patient=PatientFactory(gout=None, menopause="OMIT"),
    )
    with pytest.raises(IntegrityError):
        MedHistory.objects.create(
            patient=obj.patient,
            mhtype=obj.mhtype,
            history_of=True,
        )


@pytest.mark.django_db
def test_proxy_models_str():
    # Test __str__ for all proxy models
    for factory in [
        AnginaFactory,
        AnticoagulationFactory,
        BleedFactory,
        CadFactory,
        ChfFactory,
        CkdFactory,
        ColchicineinteractionFactory,
        DiabetesFactory,
        ErosionsFactory,
        GastricbypassFactory,
        GoutFactory,
        HeartattackFactory,
        HepatitisFactory,
        HypertensionFactory,
        HyperuricemiaFactory,
        IbdFactory,
        MenopauseFactory,
        OrgantransplantFactory,
        OsteoporosisFactory,
        PudFactory,
        PadFactory,
        StrokeFactory,
        TophiFactory,
        UratestonesFactory,
        XoiinteractionFactory,
    ]:
        obj = factory()
        s = str(obj)
        assert obj.patient.username in s
        assert str(obj.get_mhtype_display()) in s
        assert str(obj.history_of) in s
