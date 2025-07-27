import pytest
from django.db import IntegrityError
from django.db import transaction

from gouthelper_ninja.ults.choices import FlareFreqs
from gouthelper_ninja.ults.choices import FlareNums
from gouthelper_ninja.ults.choices import Indications
from gouthelper_ninja.ults.models import Ult
from gouthelper_ninja.users.tests.factories import PatientFactory

pytestmark = pytest.mark.django_db


class TestUltModel:
    def test_constraint_num_flares_valid(self):
        # Valid num_flares
        Ult.objects.create(
            num_flares=FlareNums.ZERO,
            freq_flares=None,
            indication=Indications.NOTINDICATED,
            patient=PatientFactory(),
        )
        # Invalid num_flares
        with pytest.raises(IntegrityError), transaction.atomic():
            Ult.objects.create(
                num_flares=99,  # Not in FlareNums
                freq_flares=None,
                indication=Indications.NOTINDICATED,
                patient=PatientFactory(),
            )

    def test_constraint_freq_flares_valid(self):
        # Valid freq_flares
        Ult.objects.create(
            num_flares=FlareNums.ONE,
            freq_flares=FlareFreqs.ONEORLESS,
            indication=Indications.NOTINDICATED,
            patient=PatientFactory(),
        )
        # Invalid freq_flares
        with pytest.raises(IntegrityError), transaction.atomic():
            Ult.objects.create(
                num_flares=FlareNums.ONE,
                freq_flares=99,  # Not in FlareFreqs
                indication=Indications.NOTINDICATED,
                patient=PatientFactory(),
            )
        with pytest.raises(IntegrityError), transaction.atomic():
            Ult.objects.create(
                num_flares=FlareNums.ONE,
                freq_flares=FlareFreqs.TWOORMORE,  # Not valid for ONE flares
                indication=Indications.NOTINDICATED,
                patient=PatientFactory(),
            )

    def test_constraint_indication_valid(self):
        # Valid indication
        for value in Indications.values:
            Ult.objects.create(
                num_flares=FlareNums.ONE,
                freq_flares=None,
                indication=value,
                patient=PatientFactory(),
            )
        # Invalid indication
        with pytest.raises(IntegrityError), transaction.atomic():
            Ult.objects.create(
                num_flares=FlareNums.ONE,
                freq_flares=None,
                indication=99,  # Not in Indications
                patient=PatientFactory(),
            )

    def test_constraint_freq_num_flares_valid(self):
        # Valid num_flares
        Ult.objects.create(
            num_flares=FlareNums.ZERO,
            freq_flares=None,
            indication=Indications.NOTINDICATED,
            patient=PatientFactory(),
        )
        Ult.objects.create(
            num_flares=FlareNums.ONE,
            freq_flares=FlareFreqs.ONEORLESS,
            indication=Indications.NOTINDICATED,
            patient=PatientFactory(),
        )
        Ult.objects.create(
            num_flares=FlareNums.TWOPLUS,
            freq_flares=FlareFreqs.ONEORLESS,
            indication=Indications.NOTINDICATED,
            patient=PatientFactory(),
        )
        Ult.objects.create(
            num_flares=FlareNums.TWOPLUS,
            freq_flares=FlareFreqs.TWOORMORE,
            indication=Indications.NOTINDICATED,
            patient=PatientFactory(),
        )
        # Invalid num_flares
        with pytest.raises(IntegrityError), transaction.atomic():
            Ult.objects.create(
                num_flares=99,  # Not in FlareNums
                freq_flares=None,
                indication=Indications.NOTINDICATED,
                patient=PatientFactory(),
            )
        with pytest.raises(IntegrityError), transaction.atomic():
            Ult.objects.create(
                num_flares=FlareNums.ONE,
                freq_flares=FlareFreqs.TWOORMORE,  # Not valid for ONE flares
                indication=Indications.NOTINDICATED,
                patient=PatientFactory(),
            )

    def test_historical_records(self):
        ult = Ult.objects.create(
            num_flares=FlareNums.ONE,
            freq_flares=None,
            indication=Indications.NOTINDICATED,
            patient=PatientFactory(),
        )
        assert ult.history.count() == 1
        initial_history = ult.history.first()
        assert initial_history.history_type == "+"
        assert initial_history.num_flares == FlareNums.ONE
        # Update
        ult.num_flares = FlareNums.TWOPLUS
        ult.freq_flares = FlareFreqs.ONEORLESS
        ult.save()
        expected_history_count = 2
        assert ult.history.count() == expected_history_count
        latest_history = ult.history.first()
        assert latest_history.history_type == "~"
        assert latest_history.num_flares == FlareNums.TWOPLUS
        assert ult.history.last().history_type
