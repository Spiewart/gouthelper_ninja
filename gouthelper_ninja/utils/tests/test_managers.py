from django.test import TestCase

from gouthelper_ninja.ckddetails.choices import DialysisChoices
from gouthelper_ninja.ckddetails.choices import DialysisDurations
from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.ults.choices import FlareFreqs
from gouthelper_ninja.ults.choices import FlareNums
from gouthelper_ninja.ults.models import Ult
from gouthelper_ninja.ults.schema import PatientUltEditSchema
from gouthelper_ninja.ults.schema import UltEditSchema
from gouthelper_ninja.ults.tests.factories import UltFactory
from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory


class TestGoutHelperCrudMixinRelatedModel(TestCase):
    """Tests that the GoutHelperCrudMixin creates and updates models that are related
    to the GoutHelper Patient model correctly.
    """

    def setUp(self):
        self.provider = UserFactory(role=Roles.PROVIDER)
        # PatientFactory will create Patient only Ckd and Gout.
        # Thus any additional MedHistory data processed via Ult creation or
        # update will create new related MedHistorys
        self.patient = PatientFactory(
            ckddetail={
                "dialysis": False,
                "dialysis_duration": None,
                "dialysis_type": None,
                "stage": Stages.THREE,
            },
        )
        self.ult_data = UltEditSchema(
            freq_flares=FlareFreqs.ONEORLESS,
            num_flares=FlareNums.TWOPLUS,
            patient=PatientUltEditSchema(
                id=self.patient.id,
                erosions={"history_of": False, "patient": {"id": self.patient.id}},
                tophi={"history_of": False, "patient": {"id": self.patient.id}},
                ckd={
                    "history_of": True,
                    "patient": {"id": self.patient.id, "ckddetail": None},
                },
                hyperuricemia={"history_of": False, "patient": {"id": self.patient.id}},
                uratestones={"history_of": False, "patient": {"id": self.patient.id}},
            ),
        )

    def test__gh_create(self):
        # Ult should be successfully created with correct fields
        assert Ult.objects.gh_create(
            data=self.ult_data,
        )

        ult = Ult.objects.get(patient=self.patient)

        assert isinstance(ult, Ult)
        assert ult.freq_flares == self.ult_data.freq_flares
        assert ult.num_flares == self.ult_data.num_flares
        assert ult.patient.id == self.patient.id

        # All the related MedHistorys should be created
        assert hasattr(self.patient, "erosions")
        assert hasattr(self.patient, "tophi")
        assert hasattr(self.patient, "ckddetail")
        assert hasattr(self.patient, "hyperuricemia")
        assert hasattr(self.patient, "uratestones")
        assert ult.patient.erosions.history_of is False
        assert ult.patient.tophi.history_of is False
        assert ult.patient.ckd.history_of is True
        assert ult.patient.hyperuricemia.history_of is False
        assert ult.patient.uratestones.history_of is False

        # CkdDetail should be unchanged
        assert ult.patient.ckddetail.stage == Stages.THREE
        assert ult.patient.ckddetail.dialysis is False

    def test__gh_update(self):
        ult = UltFactory(
            freq_flares=FlareFreqs.TWOORMORE,
            num_flares=FlareNums.TWOPLUS,
            patient=self.patient,
        )

        # Update the CkdDetail data so we can test that it is correctly updated
        self.ult_data.patient.ckd.patient.ckddetail = {
            "id": self.patient.ckddetail.id,
            "dialysis": True,
            "dialysis_duration": DialysisDurations.LESSTHANSIX,
            "dialysis_type": DialysisChoices.PERITONEAL,
            "stage": Stages.FIVE,
            "patient": {"id": self.patient.id},
        }

        # Ult should be successfully updated with correct fields
        assert Ult.objects.gh_update(
            instance=ult,
            data=self.ult_data,
        )

        # Ult should be successfully updated with correct fields
        assert Ult.objects.gh_update(
            instance=ult,
            data=self.ult_data,
        )

        updated_ult = Ult.objects.get(id=ult.id)

        assert isinstance(updated_ult, Ult)
        assert updated_ult.id == ult.id
        assert updated_ult.freq_flares == self.ult_data.freq_flares
        assert updated_ult.num_flares == self.ult_data.num_flares
        assert updated_ult.patient.id == self.patient.id

        # All the related MedHistorys should be created
        assert hasattr(self.patient, "erosions")
        assert hasattr(self.patient, "tophi")
        assert hasattr(self.patient, "ckddetail")
        assert hasattr(self.patient, "hyperuricemia")
        assert hasattr(self.patient, "uratestones")
        assert ult.patient.erosions.history_of is False
        assert ult.patient.tophi.history_of is False
        assert ult.patient.ckd.history_of is True
        assert ult.patient.hyperuricemia.history_of is False
        assert ult.patient.uratestones.history_of is False

        # CkdDetail should be updated
        assert updated_ult.patient.ckddetail.dialysis is True
        assert (
            updated_ult.patient.ckddetail.dialysis_duration
            == DialysisDurations.LESSTHANSIX
        )
        assert updated_ult.patient.ckddetail.dialysis_type == DialysisChoices.PERITONEAL
        assert updated_ult.patient.ckddetail.stage == Stages.FIVE
