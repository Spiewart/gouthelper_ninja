from factory import SubFactory
from factory import fuzzy
from factory.django import DjangoModelFactory

from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.models import Gender


class GenderFactory(DjangoModelFactory):
    class Meta:
        model = Gender

    gender = fuzzy.FuzzyChoice(Genders.choices, getter=lambda c: c[0])
    patient = SubFactory("apps.gouthelper_ninja.users.tests.factories.PatientFactory")
