from decimal import Decimal

import pytest
from django.test import RequestFactory
from django.test import TestCase

from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.ults.api import update_ult
from gouthelper_ninja.ults.choices import FlareFreqs
from gouthelper_ninja.ults.choices import FlareNums
from gouthelper_ninja.ults.models import Ult
from gouthelper_ninja.ults.tests.factories import UltFactory
from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestUpdateUlt(TestCase):
    def setUp(self):
        self.patient = PatientFactory(
            dateofbirth__dateofbirth=60,
            gender__gender=Genders.MALE,
            erosions=True,
            ckddetail={"stage": 3},
        )
        self.ult = UltFactory(
            freq_flares=FlareFreqs.TWOORMORE,
            num_flares=FlareNums.TWOPLUS,
            patient=self.patient,
        )
        # Patient with provider (self.provider)
        self.provider = UserFactory()
        self.patient_with_provider = PatientFactory(provider=self.provider)
        # Patient with creator (self.provider)
        self.patient_with_creator = PatientFactory(creator=self.provider)
        self.another_provider = UserFactory()
        self.admin_user = UserFactory(role=Roles.ADMIN)
        self.data = {
            "freq_flares": None,
            "num_flares": FlareNums.ZERO,
            "erosions": {"history_of": False},
            "tophi": {"history_of": True},
            "ckd": {
                "history_of": True,
                "ckddetail": {
                    "stage": 3,
                    "dateofbirth": {
                        "dateofbirth": self.patient.dateofbirth.dateofbirth,
                    },
                    "gender": {"gender": self.patient.gender.gender},
                    "baselinecreatinine": {"value": Decimal("2.0")},
                },
            },
            "hyperuricemia": {"history_of": True},
            "uratestones": {"history_of": False},
        }

    def test__updates_ult(self):
        request = RequestFactory().post("/")
        request.user = self.provider
        updated = update_ult(
            request=request,
            ult_id=self.ult.id,
            data=self.data,
        )
        assert isinstance(updated, Ult)
        assert updated.id == self.ult.id
        assert updated.freq_flares is None
        assert updated.num_flares == FlareNums.ZERO
        assert updated.patient.erosions.history_of is False
        delattr(updated.patient, "tophi")
        updated.patient.tophi.refresh_from_db()
        assert updated.patient.tophi.history_of is True
        delattr(updated.patient, "hyperuricemia")
        assert updated.patient.hyperuricemia.history_of is True
        delattr(updated.patient, "uratestones")
        assert updated.patient.uratestones.history_of is False
        assert updated.patient.ckd.history_of is True
        assert updated.patient.baselinecreatinine.value == Decimal("2.0")
        assert updated.patient.ckddetail.stage == Stages.THREE
