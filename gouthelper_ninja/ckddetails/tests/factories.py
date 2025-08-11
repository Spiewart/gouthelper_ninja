from factory import LazyAttribute
from factory import Maybe
from factory import SubFactory
from factory import fuzzy
from factory.django import DjangoModelFactory

from gouthelper_ninja.ckddetails.choices import DialysisChoices
from gouthelper_ninja.ckddetails.choices import DialysisDurations
from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.ckddetails.models import CkdDetail


class CkdDetailFactory(DjangoModelFactory):
    class Meta:
        model = CkdDetail

    stage = LazyAttribute(
        lambda o: (
            Stages.FIVE
            if o.dialysis
            else fuzzy.FuzzyChoice(
                [stage for stage in Stages if stage != Stages.__empty__],
            )
        ),
    )
    dialysis = None
    dialysis_type = Maybe(
        "dialysis",
        yes_declaration=fuzzy.FuzzyChoice(DialysisChoices),
        no_declaration=None,
    )
    dialysis_duration = Maybe(
        "dialysis",
        yes_declaration=fuzzy.FuzzyChoice(DialysisDurations),
        no_declaration=None,
    )
    patient = SubFactory(
        "gouthelper_ninja.users.tests.factories.PatientFactory",
    )
