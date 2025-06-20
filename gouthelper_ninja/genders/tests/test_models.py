import pytest
from django.db import IntegrityError
from django.urls import reverse

from gouthelper_ninja.genders.choices import Genders
from gouthelper_ninja.genders.models import Gender
from gouthelper_ninja.genders.schema import GenderEditSchema
from gouthelper_ninja.genders.tests.factories import GenderFactory
from gouthelper_ninja.users.tests.factories import PatientFactory

pytestmark = pytest.mark.django_db


class TestGenderModel:
    def test_str_representation(self):
        # Create a patient without an auto-generated gender to avoid conflicts
        patient = PatientFactory(gender=False)
        gender_obj = GenderFactory(patient=patient, gender=Genders.FEMALE.value)
        assert str(gender_obj) == Genders.FEMALE.label

    def test_get_absolute_url(self):
        # Create a patient; GenderFactory will create one if
        # gender=False is not passed to PatientFactory
        # or we create Gender explicitly.
        patient_instance = PatientFactory(gender=False)
        gender_obj = GenderFactory(patient=patient_instance)

        assert gender_obj.patient == patient_instance
        expected_url = reverse(
            "users:patient-detail",
            kwargs={"patient": patient_instance.pk},
        )
        assert gender_obj.get_absolute_url() == expected_url
        # Check that the patient's own get_absolute_url also points
        # to the patient detail view
        assert patient_instance.get_absolute_url() == expected_url

    def test_update_method_changes_gender(self):
        patient = PatientFactory(gender=False)
        gender_obj = GenderFactory(patient=patient, gender=Genders.MALE.value)
        original_gender_db_value = gender_obj.gender

        new_gender_enum = Genders.FEMALE
        # Ensure the new gender is different from the original
        if original_gender_db_value == new_gender_enum.value:
            new_gender_enum = Genders.MALE  # Should not happen with current setup

        data = GenderEditSchema(gender=new_gender_enum)
        updated_gender = gender_obj.update(data)

        assert updated_gender.gender == new_gender_enum.value
        gender_obj.refresh_from_db()
        assert gender_obj.gender == new_gender_enum.value

    def test_update_method_no_change(self):
        patient = PatientFactory(gender=False)
        original_gender_value = Genders.MALE.value
        gender_obj = GenderFactory(patient=patient, gender=original_gender_value)

        # Get the enum member corresponding to the original value for the schema
        original_gender_enum = Genders(original_gender_value)

        original_save = gender_obj.save
        save_called = False

        def mock_save(*args, **kwargs):
            nonlocal save_called
            save_called = True
            original_save(*args, **kwargs)

        gender_obj.save = mock_save

        data = GenderEditSchema(gender=original_gender_enum)
        updated_gender = gender_obj.update(data)

        assert updated_gender.gender == original_gender_value
        assert not save_called  # Save should not be called if value hasn't changed
        gender_obj.save = original_save  # Restore original save method

    def test_gender_valid_constraint_pass(self):
        patient = PatientFactory(gender=False)
        try:
            GenderFactory(patient=patient, gender=Genders.FEMALE.value)
        except IntegrityError:  # pragma: no cover
            pytest.fail("IntegrityError raised for valid gender")

    def test_gender_valid_constraint_fail(self):
        patient = PatientFactory(gender=False)  # Patient without auto-gender
        with pytest.raises(IntegrityError):
            # Directly try to create a Gender with an invalid integer value
            Gender.objects.create(
                patient=patient,
                gender=99,
            )  # 99 is not in Genders.values

    def test_historical_records(self):
        patient = PatientFactory(gender=False)
        original_gender_value = Genders.MALE.value
        gender_obj = GenderFactory(patient=patient, gender=original_gender_value)

        # Check history after initial creation by factory
        assert gender_obj.history.count() == 1
        initial_history = gender_obj.history.first()
        assert initial_history.history_type == "+"
        assert initial_history.gender == original_gender_value

        new_gender_enum = Genders.FEMALE
        if original_gender_value == new_gender_enum.value:  # pragma: no cover
            new_gender_enum = Genders.MALE  # Should not happen

        data = GenderEditSchema(gender=new_gender_enum)
        gender_obj.update(data)  # This calls save if changed

        expected_history_count = 2
        assert gender_obj.history.count() == expected_history_count
        latest_history = gender_obj.history.first()  # Most recent
        assert latest_history.history_type == "~"  # '~' indicates an update
        assert latest_history.gender == new_gender_enum.value
        assert gender_obj.history.last().history_type == "+"  # Oldest (creation)
