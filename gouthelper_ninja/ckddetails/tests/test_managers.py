from uuid import uuid4

import pytest

from gouthelper_ninja.ckddetails.choices import DialysisChoices
from gouthelper_ninja.ckddetails.choices import DialysisDurations
from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.ckddetails.models import CkdDetail
from gouthelper_ninja.ckddetails.schema import CkdDetailEditSchema
from gouthelper_ninja.users.tests.factories import PatientFactory

pytestmark = pytest.mark.django_db


class TestCkdDetailManager:
    def test_gh_create_creates_ckddetail(self):
        patient = PatientFactory()
        schema = CkdDetailEditSchema(
            dialysis=False,
            dialysis_duration=None,
            dialysis_type=None,
            stage=Stages.THREE,
            age=None,
            creatinine=None,
            gender=None,
        )

        created = CkdDetail.objects.gh_create(schema, patient_id=patient.id)

        assert isinstance(created, CkdDetail)
        assert created.patient_id == patient.id
        assert created.stage == Stages.THREE
        assert created.dialysis is False

    def test_gh_create_with_dialysis(self):
        patient = PatientFactory()
        schema = CkdDetailEditSchema(
            dialysis=True,
            dialysis_duration=DialysisDurations.LESSTHANSIX,
            dialysis_type=DialysisChoices.HEMODIALYSIS,
            stage=Stages.FIVE,
            age=None,
            creatinine=None,
            gender=None,
        )

        created = CkdDetail.objects.gh_create(schema, patient_id=patient.id)

        assert created.dialysis is True
        assert created.dialysis_type == DialysisChoices.HEMODIALYSIS
        assert created.stage == Stages.FIVE

    def test_gh_create_requires_schema_like_object(self):
        # Passing a plain dict should raise because dict has no model_dump()
        with pytest.raises(AttributeError):
            CkdDetail.objects.gh_create({"stage": Stages.ONE}, patient_id=uuid4())

    def test_schema_validation_runs_before_create(self):
        # Creating an invalid schema (dialysis True but no dialysis_type)
        with pytest.raises(ValueError, match="must be provided if dialysis is True"):
            CkdDetailEditSchema(
                dialysis=True,
                dialysis_duration=None,
                dialysis_type=None,
                stage=Stages.FIVE,
            )
