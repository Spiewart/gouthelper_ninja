from factory import SubFactory
from factory import fuzzy
from factory.django import DjangoModelFactory
from factory.faker import faker

from gouthelper_ninja.ults.choices import FlareFreqs
from gouthelper_ninja.ults.choices import FlareNums
from gouthelper_ninja.ults.models import Ult

fake = faker.Faker()


class UltFactory(DjangoModelFactory):
    class Meta:
        model = Ult

    num_flares = fuzzy.FuzzyChoice(FlareNums.values)
    freq_flares = fuzzy.FuzzyChoice(FlareFreqs.values)
    patient = SubFactory(
        "gouthelper_ninja.users.tests.factories.PatientFactory",
        ult=None,
    )
