from factory import SubFactory
from factory import fuzzy
from factory.django import DjangoModelFactory

from gouthelper_ninja.labs.choices import CreatinineLimits
from gouthelper_ninja.labs.choices import Units
from gouthelper_ninja.labs.models import BaselineCreatinine


class BaselineCreatinineFactory(DjangoModelFactory):
    class Meta:
        model = BaselineCreatinine

    lower_limit = CreatinineLimits.LOWERMGDL
    units = Units.MGDL
    upper_limit = CreatinineLimits.UPPERMGDL
    value = fuzzy.FuzzyDecimal(
        low=0.50,
        high=5.00,
        precision=2,
    )
    patient = SubFactory(
        "gouthelper_ninja.users.tests.factories.PatientFactory",
        baselinecreatinine=None,
    )
