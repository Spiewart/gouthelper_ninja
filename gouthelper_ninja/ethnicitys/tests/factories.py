from factory import SubFactory
from factory import fuzzy
from factory.django import DjangoModelFactory

from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.ethnicitys.models import Ethnicity


class EthnicityFactory(DjangoModelFactory):
    class Meta:
        model = Ethnicity

    ethnicity = fuzzy.FuzzyChoice(Ethnicitys.choices, getter=lambda c: c[0])
    patient = SubFactory(
        "apps.gouthelper_ninja.users.tests.factories.PatientFactory",
        ethnicity=None,
    )
