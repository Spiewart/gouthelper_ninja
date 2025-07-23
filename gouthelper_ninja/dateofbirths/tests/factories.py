from datetime import date

from factory import Faker
from factory import SubFactory
from factory import Transformer
from factory.django import DjangoModelFactory

from gouthelper_ninja.dateofbirths.models import DateOfBirth
from gouthelper_ninja.utils.helpers import yearsago_date


class DateOfBirthFactory(DjangoModelFactory):
    class Meta:
        model = DateOfBirth

    dateofbirth = Transformer(
        Faker("date_of_birth", minimum_age=18, maximum_age=100),
        transform=lambda x: (
            yearsago_date(x)
            if isinstance(x, int)
            else date(*map(int, x.split("-")))
            if isinstance(x, str)
            else x
        ),
    )
    patient = SubFactory(
        "gouthelper_ninja.users.tests.factories.PatientFactory",
        dateofbirth=False,
    )
