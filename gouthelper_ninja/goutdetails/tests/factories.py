from factory import Maybe
from factory import SubFactory
from factory import fuzzy
from factory.django import DjangoModelFactory

from gouthelper_ninja.goutdetails.models import GoutDetail


class GoutDetailFactory(DjangoModelFactory):
    class Meta:
        model = GoutDetail

    at_goal = fuzzy.FuzzyChoice([True, False, None])
    at_goal_long_term = Maybe(
        "at_goal",
        yes_declaration=fuzzy.FuzzyChoice([True, False]),
        no_declaration=False,
    )
    flaring = fuzzy.FuzzyChoice([True, False, None])
    on_ppx = fuzzy.FuzzyChoice([True, False])
    on_ult = fuzzy.FuzzyChoice([True, False])
    starting_ult = fuzzy.FuzzyChoice([True, False])
    patient = SubFactory(
        "gouthelper_ninja.users.tests.factories.PatientFactory",
        goutdetail=None,
    )
