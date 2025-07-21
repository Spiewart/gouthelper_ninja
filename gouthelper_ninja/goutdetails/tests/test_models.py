import pytest
from django.db import IntegrityError
from django.db import transaction

from gouthelper_ninja.goutdetails.models import GoutDetail
from gouthelper_ninja.goutdetails.schema import GoutDetailEditSchema
from gouthelper_ninja.goutdetails.tests.factories import GoutDetailFactory
from gouthelper_ninja.users.tests.factories import PatientFactory

pytestmark = pytest.mark.django_db


class TestGoutDetailModel:
    def test_get_absolute_url(self):
        patient = PatientFactory()
        gout_detail = patient.goutdetail
        expected_url = patient.get_absolute_url()
        assert gout_detail.get_absolute_url() == expected_url

    def test_update_method_changes_fields(self):
        patient = PatientFactory(goutdetail__at_goal=False, goutdetail__flaring=True)
        gout_detail = patient.goutdetail
        data = GoutDetailEditSchema(at_goal=True, flaring=False)
        updated = gout_detail.update(data)
        assert updated.at_goal is True
        assert updated.flaring is False
        gout_detail.refresh_from_db()
        assert gout_detail.at_goal is True
        assert gout_detail.flaring is False

    def test_update_method_no_change(self):
        patient = PatientFactory(goutdetail=False)
        gout_detail = GoutDetailFactory(patient=patient, at_goal=True)
        data = GoutDetailEditSchema(
            at_goal=True,
            at_goal_long_term=gout_detail.at_goal_long_term,
            flaring=gout_detail.flaring,
            on_ppx=gout_detail.on_ppx,
            on_ult=gout_detail.on_ult,
            starting_ult=gout_detail.starting_ult,
        )
        original_save = gout_detail.save
        save_called = False

        def mock_save(*args, **kwargs):
            nonlocal save_called
            save_called = True
            original_save(*args, **kwargs)

        gout_detail.save = mock_save
        updated = gout_detail.update(data)
        assert updated.at_goal is True
        assert not save_called
        gout_detail.save = original_save

    def test_constraint_at_goal_valid(self):
        # Valid: at_goal=False, at_goal_long_term=False
        try:
            GoutDetail.objects.create(
                at_goal=False,
                at_goal_long_term=False,
                patient=PatientFactory(goutdetail=False),
            )
        except IntegrityError:
            pytest.fail("IntegrityError raised for valid at_goal/at_goal_long_term")
        # Valid: at_goal=True noqa: ERA001
        try:
            GoutDetail.objects.create(
                at_goal=True,
                patient=PatientFactory(goutdetail=False),
            )
        except IntegrityError:
            pytest.fail("IntegrityError raised for valid at_goal=True")
        # Invalid: at_goal=None, at_goal_long_term=True
        with pytest.raises(IntegrityError) as _, transaction.atomic() as _:
            GoutDetail(
                at_goal=None,
                at_goal_long_term=True,
                patient=PatientFactory(goutdetail=False),
            ).save()
        # Invalid: at_goal=False, at_goal_long_term=True
        with pytest.raises(IntegrityError) as _, transaction.atomic() as _:
            GoutDetail(
                at_goal=False,
                at_goal_long_term=True,
                patient=PatientFactory(goutdetail=False),
            ).save()

    def test_historical_records(self):
        patient = PatientFactory(goutdetail=False)
        gout_detail = GoutDetailFactory(patient=patient, at_goal=False)
        expected_history_count = 1
        assert gout_detail.history.count() == expected_history_count
        initial_history = gout_detail.history.first()
        assert initial_history.history_type == "+"
        assert initial_history.at_goal is False
        # Update
        data = GoutDetailEditSchema(at_goal=True)
        gout_detail.update(data)
        expected_history_count = 2
        assert gout_detail.history.count() == expected_history_count
        latest_history = gout_detail.history.first()
        assert latest_history.history_type == "~"
        assert latest_history.at_goal is True
        assert gout_detail.history.last().history_type == "+"
