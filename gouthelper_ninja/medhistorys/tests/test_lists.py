from gouthelper_ninja.medhistorys.choices import MedHistoryTypes
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
    assert MedHistoryTypes.ANGINA in CV_DISEASES
    assert MedHistoryTypes.CAD in CV_DISEASES
    assert MedHistoryTypes.CHF in CV_DISEASES
    assert MedHistoryTypes.HEARTATTACK in CV_DISEASES
    assert MedHistoryTypes.STROKE in CV_DISEASES
    assert MedHistoryTypes.PVD in CV_DISEASES
    assert MedHistoryTypes.HYPERTENSION not in CV_DISEASES


def test_goalurate_medhistorys_contents():
    assert GOALURATE_MEDHISTORYS == [
        MedHistoryTypes.EROSIONS,
        MedHistoryTypes.TOPHI,
    ]


def test_flare_medhistorys_contents():
    expected = [
        MedHistoryTypes.ANGINA,
        MedHistoryTypes.CAD,
        MedHistoryTypes.CHF,
        MedHistoryTypes.CKD,
        MedHistoryTypes.GOUT,
        MedHistoryTypes.HEARTATTACK,
        MedHistoryTypes.HYPERTENSION,
        MedHistoryTypes.MENOPAUSE,
        MedHistoryTypes.PVD,
        MedHistoryTypes.STROKE,
    ]
    assert expected == FLARE_MEDHISTORYS


def test_flareaid_medhistorys_contents():
    assert MedHistoryTypes.ANTICOAGULATION in FLAREAID_MEDHISTORYS
    assert MedHistoryTypes.BLEED in FLAREAID_MEDHISTORYS
    assert MedHistoryTypes.COLCHICINEINTERACTION in FLAREAID_MEDHISTORYS
    assert MedHistoryTypes.PUD in FLAREAID_MEDHISTORYS
    assert MedHistoryTypes.STROKE in FLAREAID_MEDHISTORYS
    assert MedHistoryTypes.GOUT not in FLAREAID_MEDHISTORYS


def test_other_nsaid_contras_contents():
    expected = [
        MedHistoryTypes.ANTICOAGULATION,
        MedHistoryTypes.BLEED,
        MedHistoryTypes.GASTRICBYPASS,
        MedHistoryTypes.IBD,
        MedHistoryTypes.PUD,
    ]
    assert expected == OTHER_NSAID_CONTRAS


def test_ppx_medhistorys_contents():
    assert PPX_MEDHISTORYS == [MedHistoryTypes.GOUT]


def test_ppxaid_medhistorys_contents():
    assert MedHistoryTypes.ANGINA in PPXAID_MEDHISTORYS
    assert MedHistoryTypes.BLEED in PPXAID_MEDHISTORYS
    assert MedHistoryTypes.PUD in PPXAID_MEDHISTORYS
    assert MedHistoryTypes.STROKE in PPXAID_MEDHISTORYS
    assert MedHistoryTypes.GOUT not in PPXAID_MEDHISTORYS


def test_ult_medhistorys_contents():
    expected = [
        MedHistoryTypes.CKD,
        MedHistoryTypes.EROSIONS,
        MedHistoryTypes.HYPERURICEMIA,
        MedHistoryTypes.TOPHI,
        MedHistoryTypes.URATESTONES,
    ]
    assert expected == ULT_MEDHISTORYS


def test_ultaid_medhistorys_contents():
    assert MedHistoryTypes.ANGINA in ULTAID_MEDHISTORYS
    assert MedHistoryTypes.CAD in ULTAID_MEDHISTORYS
    assert MedHistoryTypes.HEPATITIS in ULTAID_MEDHISTORYS
    assert MedHistoryTypes.XOIINTERACTION in ULTAID_MEDHISTORYS
    assert MedHistoryTypes.GOUT not in ULTAID_MEDHISTORYS
