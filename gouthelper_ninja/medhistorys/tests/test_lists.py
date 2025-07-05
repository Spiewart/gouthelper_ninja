from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.medhistorys.lists import CV_DISEASES
from gouthelper_ninja.medhistorys.lists import FLARE_MEDHISTORYS
from gouthelper_ninja.medhistorys.lists import FLAREAID_MEDHISTORYS
from gouthelper_ninja.medhistorys.lists import GOALURATE_MEDHISTORYS
from gouthelper_ninja.medhistorys.lists import OTHER_NSAID_CONTRAS
from gouthelper_ninja.medhistorys.lists import PPX_MEDHISTORYS
from gouthelper_ninja.medhistorys.lists import PPXAID_MEDHISTORYS
from gouthelper_ninja.medhistorys.lists import ULT_MEDHISTORYS
from gouthelper_ninja.medhistorys.lists import ULTAID_MEDHISTORYS


def test_cv_diseases_contents() -> None:
    assert MHTypes.ANGINA in CV_DISEASES
    assert MHTypes.CAD in CV_DISEASES
    assert MHTypes.CHF in CV_DISEASES
    assert MHTypes.HEARTATTACK in CV_DISEASES
    assert MHTypes.STROKE in CV_DISEASES
    assert MHTypes.PAD in CV_DISEASES
    assert MHTypes.HYPERTENSION not in CV_DISEASES


def test_goalurate_medhistorys_contents():
    assert GOALURATE_MEDHISTORYS == [
        MHTypes.EROSIONS,
        MHTypes.TOPHI,
    ]


def test_flare_medhistorys_contents():
    expected = [
        MHTypes.ANGINA,
        MHTypes.CAD,
        MHTypes.CHF,
        MHTypes.CKD,
        MHTypes.GOUT,
        MHTypes.HEARTATTACK,
        MHTypes.HYPERTENSION,
        MHTypes.MENOPAUSE,
        MHTypes.PAD,
        MHTypes.STROKE,
    ]
    assert expected == FLARE_MEDHISTORYS


def test_flareaid_medhistorys_contents():
    assert MHTypes.ANTICOAGULATION in FLAREAID_MEDHISTORYS
    assert MHTypes.BLEED in FLAREAID_MEDHISTORYS
    assert MHTypes.COLCHICINEINTERACTION in FLAREAID_MEDHISTORYS
    assert MHTypes.PUD in FLAREAID_MEDHISTORYS
    assert MHTypes.STROKE in FLAREAID_MEDHISTORYS
    assert MHTypes.GOUT not in FLAREAID_MEDHISTORYS


def test_other_nsaid_contras_contents():
    expected = [
        MHTypes.ANTICOAGULATION,
        MHTypes.BLEED,
        MHTypes.GASTRICBYPASS,
        MHTypes.IBD,
        MHTypes.PUD,
    ]
    assert expected == OTHER_NSAID_CONTRAS


def test_ppx_medhistorys_contents():
    assert PPX_MEDHISTORYS == [MHTypes.GOUT]


def test_ppxaid_medhistorys_contents():
    assert MHTypes.ANGINA in PPXAID_MEDHISTORYS
    assert MHTypes.BLEED in PPXAID_MEDHISTORYS
    assert MHTypes.PUD in PPXAID_MEDHISTORYS
    assert MHTypes.STROKE in PPXAID_MEDHISTORYS
    assert MHTypes.GOUT not in PPXAID_MEDHISTORYS


def test_ult_medhistorys_contents():
    expected = [
        MHTypes.CKD,
        MHTypes.EROSIONS,
        MHTypes.HYPERURICEMIA,
        MHTypes.TOPHI,
        MHTypes.URATESTONES,
    ]
    assert expected == ULT_MEDHISTORYS


def test_ultaid_medhistorys_contents():
    assert MHTypes.ANGINA in ULTAID_MEDHISTORYS
    assert MHTypes.CAD in ULTAID_MEDHISTORYS
    assert MHTypes.HEPATITIS in ULTAID_MEDHISTORYS
    assert MHTypes.XOIINTERACTION in ULTAID_MEDHISTORYS
    assert MHTypes.GOUT not in ULTAID_MEDHISTORYS
