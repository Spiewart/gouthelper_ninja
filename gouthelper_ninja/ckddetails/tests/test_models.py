import pytest
from django.db import IntegrityError
from django.db import transaction

from gouthelper_ninja.ckddetails.choices import DialysisChoices
from gouthelper_ninja.ckddetails.choices import DialysisDurations
from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.ckddetails.models import CkdDetail
from gouthelper_ninja.users.tests.factories import PatientFactory

pytestmark = pytest.mark.django_db


class TestCkdDetailModel:
    def test_constraint_dialysis_valid(self):
        # Valid: Not on dialysis
        CkdDetail.objects.create(
            patient=PatientFactory(),
            dialysis=False,
            dialysis_duration=None,
            dialysis_type=None,
            stage=Stages.THREE,
        )
        # Valid: On dialysis with stage 5
        CkdDetail.objects.create(
            patient=PatientFactory(),
            dialysis=True,
            dialysis_duration=DialysisDurations.LESSTHANSIX,
            dialysis_type=DialysisChoices.HEMODIALYSIS,
            stage=Stages.FIVE,
        )
        # Invalid: On dialysis but not stage 5
        with pytest.raises(IntegrityError), transaction.atomic():
            CkdDetail.objects.create(
                patient=PatientFactory(),
                dialysis=True,
                dialysis_duration=DialysisDurations.LESSTHANSIX,
                dialysis_type=DialysisChoices.HEMODIALYSIS,
                stage=Stages.THREE,
            )
        # Invalid: Not on dialysis but dialysis fields are set
        with pytest.raises(IntegrityError), transaction.atomic():
            CkdDetail.objects.create(
                patient=PatientFactory(),
                dialysis=False,
                dialysis_duration=DialysisDurations.LESSTHANSIX,
                dialysis_type=DialysisChoices.HEMODIALYSIS,
                stage=Stages.THREE,
            )

    def test_constraint_dialysis_duration_valid(self):
        # Valid dialysis durations
        for value in DialysisDurations.values:
            CkdDetail.objects.create(
                patient=PatientFactory(),
                dialysis=True,
                dialysis_duration=value,
                dialysis_type=DialysisChoices.HEMODIALYSIS,
                stage=Stages.FIVE,
            )
        # Invalid dialysis duration
        with pytest.raises(IntegrityError), transaction.atomic():
            CkdDetail.objects.create(
                patient=PatientFactory(),
                dialysis=True,
                dialysis_duration=99,  # Not in DialysisDurations
                dialysis_type=DialysisChoices.HEMODIALYSIS,
                stage=Stages.FIVE,
            )

    def test_constraint_dialysis_type_valid(self):
        # Valid dialysis types
        for value in DialysisChoices.values:
            CkdDetail.objects.create(
                patient=PatientFactory(),
                dialysis=True,
                dialysis_duration=DialysisDurations.LESSTHANSIX,
                dialysis_type=value,
                stage=Stages.FIVE,
            )
        # Invalid dialysis type
        with pytest.raises(IntegrityError), transaction.atomic():
            CkdDetail.objects.create(
                patient=PatientFactory(),
                dialysis=True,
                dialysis_duration=DialysisDurations.LESSTHANSIX,
                dialysis_type=99,  # Not in DialysisChoices
                stage=Stages.FIVE,
            )

    def test_constraint_stage_valid(self):
        # Valid stages
        for value in [stage for stage in Stages.values if stage]:
            CkdDetail.objects.create(
                patient=PatientFactory(),
                dialysis=False,
                dialysis_duration=None,
                dialysis_type=None,
                stage=value,
            )
        # Invalid stage
        with pytest.raises(IntegrityError), transaction.atomic():
            CkdDetail.objects.create(
                patient=PatientFactory(),
                dialysis=False,
                dialysis_duration=None,
                dialysis_type=None,
                stage=99,  # Not in Stages
            )

    def test_explanation_property(self):
        # Test explanation for dialysis
        ckd_detail = CkdDetail.objects.create(
            patient=PatientFactory(),
            dialysis=True,
            dialysis_duration=DialysisDurations.LESSTHANSIX,
            dialysis_type=DialysisChoices.PERITONEAL,
            stage=Stages.FIVE,
        )
        assert ckd_detail.explanation == "CKD on peritoneal dialysis"
        # Test explanation for non-dialysis
        ckd_detail.dialysis = False
        ckd_detail.dialysis_duration = None
        ckd_detail.dialysis_type = None
        ckd_detail.stage = Stages.THREE
        ckd_detail.save()
        assert ckd_detail.explanation == "CKD stage III"

    def test_historical_records(self):
        patient = PatientFactory()
        ckd_detail = CkdDetail.objects.create(
            patient=patient,
            dialysis=False,
            dialysis_duration=None,
            dialysis_type=None,
            stage=Stages.THREE,
        )
        assert ckd_detail.history.count() == 1
        initial_history = ckd_detail.history.first()
        assert initial_history.history_type == "+"
        assert initial_history.stage == Stages.THREE
        # Update
        ckd_detail.stage = Stages.FOUR
        ckd_detail.save()
        expected_num_history = 2
        assert ckd_detail.history.count() == expected_num_history
        latest_history = ckd_detail.history.first()
        assert latest_history.history_type == "~"
        assert latest_history.stage == Stages.FOUR
