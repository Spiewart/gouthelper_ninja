from factory import LazyAttribute
from factory import SubFactory
from factory.django import DjangoModelFactory

from gouthelper_ninja.profiles.helpers import get_provider_alias
from gouthelper_ninja.profiles.models import PatientProfile
from gouthelper_ninja.profiles.models import ProviderProfile
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory
from gouthelper_ninja.utils.helpers import age_calc


class PatientProfileFactory(DjangoModelFactory):
    class Meta:
        model = PatientProfile

    user = SubFactory(PatientFactory)
    provider = SubFactory(UserFactory)
    provider_alias = LazyAttribute(
        lambda o: get_provider_alias(
            provider_id=o.provider,
            age=age_calc(o.user.dateofbirth.dateobirth),
            gender=o.user.gender.gender,
        )
        if (o.provider and o.user.dateofbirth and o.user.gender)
        else None,
    )


class ProviderProfileFactory(DjangoModelFactory):
    class Meta:
        model = ProviderProfile
