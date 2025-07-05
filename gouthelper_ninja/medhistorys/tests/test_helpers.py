from unittest.mock import MagicMock

import pytest

from gouthelper_ninja.medhistorys.helpers import search_medhistorys_by_mhtype


class DummyMedHistory:
    def __init__(self, mhtype):
        self.mhtype = mhtype


@pytest.fixture
def medhistory_types():
    class MHTypes:
        TYPE_A = "A"
        TYPE_B = "B"

    return MHTypes


def test_search_medhistorys_by_mhtype_returns_first_match(medhistory_types):
    mh1 = DummyMedHistory(medhistory_types.TYPE_A)
    mh2 = DummyMedHistory(medhistory_types.TYPE_B)
    mh3 = DummyMedHistory(medhistory_types.TYPE_A)
    medhistorys = [mh2, mh1, mh3]
    result = search_medhistorys_by_mhtype(medhistorys, medhistory_types.TYPE_A)
    assert result is mh1


def test_search_medhistorys_by_mhtype_returns_none_if_no_match(medhistory_types):
    mh1 = DummyMedHistory(medhistory_types.TYPE_B)
    medhistorys = [mh1]
    result = search_medhistorys_by_mhtype(medhistorys, medhistory_types.TYPE_A)
    assert result is None


def test_search_medhistorys_by_mhtype_returns_none_if_empty(medhistory_types):
    medhistorys = []
    result = search_medhistorys_by_mhtype(medhistorys, medhistory_types.TYPE_A)
    assert result is None


def test_search_medhistorys_by_mhtype_works_with_queryset_like(medhistory_types):
    mh1 = DummyMedHistory(medhistory_types.TYPE_B)
    mh2 = DummyMedHistory(medhistory_types.TYPE_A)
    queryset = MagicMock()
    queryset.__iter__.return_value = iter([mh1, mh2])
    result = search_medhistorys_by_mhtype(queryset, medhistory_types.TYPE_A)
    assert result is mh2
