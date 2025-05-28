from factory.django import DjangoModelFactory

from gouthelper_ninja.profiles.models import PatientProfile
from gouthelper_ninja.profiles.models import ProviderProfile


class PatientProfileFactory(DjangoModelFactory):
    class Meta:
        model = PatientProfile


class ProviderProfileFactory(DjangoModelFactory):
    class Meta:
        model = ProviderProfile
