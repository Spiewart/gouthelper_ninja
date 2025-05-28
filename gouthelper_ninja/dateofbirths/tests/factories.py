from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory

from gouthelper_ninja.dateofbirths.models import DateOfBirth


class DateOfBirthFactory(DjangoModelFactory):
    class Meta:
        model = DateOfBirth

    dateofbirth = Faker("date_of_birth", minimum_age=18, maximum_age=100)
    patient = SubFactory("apps.gouthelper_ninja.users.tests.factories.PatientFactory")
