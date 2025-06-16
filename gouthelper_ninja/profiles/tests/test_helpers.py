from datetime import date

import pytest
from freezegun import freeze_time

from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.profiles.helpers import get_provider_alias
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestGetProviderAlias:
    @freeze_time("2023-10-26")
    def test_get_provider_alias_no_existing_patients_today(self):
        provider = UserFactory()
        # Patient created yesterday for the same provider, should not count
        with freeze_time("2023-10-25"):
            PatientFactory(
                provider=provider,
                dateofbirth=30,  # Results in age 30 on 2023-10-25
                gender=Genders.MALE,
            )

        alias = get_provider_alias(
            provider_id=provider.id,
            age=30,
            gender=Genders.MALE,
        )
        assert alias == 1, "Alias should be 1 when no matching patients exist today"

    @freeze_time("2023-10-26 12:00:00")
    def test_get_provider_alias_one_existing_patient_today_same_criteria(self):
        provider = UserFactory()
        PatientFactory(
            provider=provider,
            dateofbirth=30,  # Results in age 30 on 2023-10-26
            gender=Genders.MALE,
        )  # Created today due to outer freeze_time

        alias = get_provider_alias(
            provider_id=provider.id,
            age=30,
            gender=Genders.MALE,
        )
        assert alias == 2, "Alias should be 2 (1 existing + 1)"  # noqa: PLR2004

    @freeze_time("2023-10-26 12:00:00")
    def test_get_provider_alias_multiple_existing_patients_today_same_criteria(self):
        provider = UserFactory()
        PatientFactory(
            provider=provider,
            dateofbirth=30,
            gender=Genders.MALE,
        )
        PatientFactory(
            provider=provider,
            dateofbirth=30,
            gender=Genders.MALE,
        )

        alias = get_provider_alias(
            provider_id=provider.id,
            age=30,
            gender=Genders.MALE,
        )
        assert alias == 3, "Alias should be 3 (2 existing + 1)"  # noqa: PLR2004

    @freeze_time("2023-10-26 12:00:00")
    def test_get_provider_alias_existing_patient_today_different_age(self):
        provider = UserFactory()
        PatientFactory(
            provider=provider,
            dateofbirth=35,  # Age 35
            gender=Genders.MALE,
        )

        alias = get_provider_alias(
            provider_id=provider.id,
            age=30,  # Requesting for age 30
            gender=Genders.MALE,
        )
        assert alias == 1, "Patient with different age should not count"

    @freeze_time("2023-10-26")
    def test_get_provider_alias_existing_patient_today_different_gender(self):
        provider = UserFactory()
        PatientFactory(
            provider=provider,
            dateofbirth=30,
            gender=Genders.FEMALE,  # Female
        )

        alias = get_provider_alias(
            provider_id=provider.id,
            age=30,
            gender=Genders.MALE,  # Requesting for Male
        )
        assert alias == 1, "Patient with different gender should not count"

    @freeze_time("2023-10-26")
    def test_get_provider_alias_existing_patient_different_day_same_criteria(self):
        provider = UserFactory()

        with freeze_time(date(2023, 10, 25)):  # Patient created yesterday
            PatientFactory(
                provider=provider,
                dateofbirth=30,
                gender=Genders.MALE,
            )

        alias = get_provider_alias(
            provider_id=provider.id,
            age=30,
            gender=Genders.MALE,
        )
        assert alias == 1, "Patient created on a different day should not count"

    @freeze_time("2023-10-26")
    def test_get_provider_alias_existing_patient_different_provider_same_criteria(self):
        provider1 = UserFactory()
        provider2 = UserFactory()

        PatientFactory(
            provider=provider2,  # Belongs to provider2
            dateofbirth=30,
            gender=Genders.MALE,
        )

        alias = get_provider_alias(
            provider_id=provider1.id,  # Requesting for provider1
            age=30,
            gender=Genders.MALE,
        )
        assert alias == 1, "Patient with different provider should not count"

    @freeze_time("2023-10-26")
    def test_get_provider_alias_no_patients_for_provider(self):
        provider_with_no_patients = UserFactory()
        # Create a patient for another provider to ensure DB isn't empty
        PatientFactory(provider=UserFactory(), dateofbirth=25, gender=Genders.FEMALE)

        alias = get_provider_alias(
            provider_id=provider_with_no_patients.id,
            age=25,
            gender=Genders.FEMALE,
        )
        assert alias == 1, (
            "Alias should be 1 if the provider has no patients today matching criteria"
        )
