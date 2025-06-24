from factory import SubFactory
from factory.django import DjangoModelFactory

from gouthelper_ninja.profiles.models import PatientProfile
from gouthelper_ninja.profiles.models import ProviderProfile


class PatientProfileFactory(DjangoModelFactory):
    class Meta:
        model = PatientProfile

    user = SubFactory("gouthelper_ninja.users.tests.factories.PatientFactory")


class ProviderProfileFactory(DjangoModelFactory):
    class Meta:
        model = ProviderProfile
