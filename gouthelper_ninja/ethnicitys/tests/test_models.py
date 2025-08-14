import pytest
from django.db import IntegrityError
from django.urls import reverse

from gouthelper_ninja.ethnicitys.choices import Ethnicitys
from gouthelper_ninja.ethnicitys.models import Ethnicity
from gouthelper_ninja.ethnicitys.schema import EthnicityEditSchema
from gouthelper_ninja.ethnicitys.tests.factories import EthnicityFactory
from gouthelper_ninja.users.tests.factories import PatientFactory

pytestmark = pytest.mark.django_db


class TestEthnicityModel:
    def test_str_representation(self):
        # Create a patient without an auto-generated ethnicity to avoid conflicts
        patient = PatientFactory(ethnicity=False)
        ethnicity_obj = EthnicityFactory(
            patient=patient,
            ethnicity=Ethnicitys.CAUCASIAN.value,
        )
        assert str(ethnicity_obj) == Ethnicitys.CAUCASIAN.label

    def test_get_absolute_url(self):
        patient_instance = PatientFactory(ethnicity=False)
        ethnicity_obj = EthnicityFactory(patient=patient_instance)

        assert ethnicity_obj.patient == patient_instance
        expected_url = reverse(
            "users:patient-detail",
            kwargs={"patient": patient_instance.pk},
        )
        assert ethnicity_obj.get_absolute_url() == expected_url
        # Check that the patient's own get_absolute_url also
        # points to the patient detail view
        assert patient_instance.get_absolute_url() == expected_url

    def test_update_method_changes_ethnicity(self):
        patient = PatientFactory(ethnicity=False)
        ethnicity_obj = EthnicityFactory(
            patient=patient,
            ethnicity=Ethnicitys.AFRICANAMERICAN.value,
        )
        original_ethnicity_db_value = ethnicity_obj.ethnicity

        new_ethnicity_enum = Ethnicitys.HMONG
        # Ensure the new ethnicity is different from the original
        if original_ethnicity_db_value == new_ethnicity_enum.value:
            new_ethnicity_enum = Ethnicitys.KOREAN  # Pick another different one

        data = EthnicityEditSchema(ethnicity=new_ethnicity_enum)
        updated_ethnicity = ethnicity_obj.gh_update(data)

        assert updated_ethnicity.ethnicity == new_ethnicity_enum.value
        ethnicity_obj.refresh_from_db()
        assert ethnicity_obj.ethnicity == new_ethnicity_enum.value

    def test_update_method_no_change(self):
        patient = PatientFactory(ethnicity=False)
        original_ethnicity_value = Ethnicitys.CAUCASIAN.value
        ethnicity_obj = EthnicityFactory(
            patient=patient,
            ethnicity=original_ethnicity_value,
        )

        # Get the enum member corresponding to the original value for the schema
        original_ethnicity_enum = Ethnicitys(original_ethnicity_value)

        original_save = ethnicity_obj.save
        save_called = False

        def mock_save(*args, **kwargs):
            nonlocal save_called
            save_called = True
            original_save(*args, **kwargs)

        ethnicity_obj.save = mock_save

        data = EthnicityEditSchema(ethnicity=original_ethnicity_enum)
        updated_ethnicity = ethnicity_obj.gh_update(data)

        assert updated_ethnicity.ethnicity == original_ethnicity_value
        assert not save_called
        ethnicity_obj.save = original_save  # Restore original save method

    def test_ethnicity_valid_constraint_pass(self):
        patient = PatientFactory(ethnicity=False)
        try:
            EthnicityFactory(patient=patient, ethnicity=Ethnicitys.KOREAN.value)
        except IntegrityError:  # pragma: no cover
            pytest.fail("IntegrityError raised for valid ethnicity")

    def test_ethnicity_valid_constraint_fail(self):
        patient = PatientFactory(ethnicity=False)  # Patient without auto-ethnicity
        with pytest.raises(IntegrityError):
            # Directly try to create an Ethnicity with an invalid string value
            Ethnicity.objects.create(
                patient=patient,
                ethnicity="INVALID_ETHNICITY_CODE",
            )

    def test_historical_records(self):
        patient = PatientFactory(ethnicity=False)
        original_ethnicity_value = Ethnicitys.HISPANIC.value
        ethnicity_obj = EthnicityFactory(
            patient=patient,
            ethnicity=original_ethnicity_value,
        )

        # Check history after initial creation by factory
        assert ethnicity_obj.history.count() == 1
        initial_history = ethnicity_obj.history.first()
        assert initial_history.history_type == "+"
        assert initial_history.ethnicity == original_ethnicity_value

        new_ethnicity_enum = Ethnicitys.PACIFICISLANDER
        if original_ethnicity_value == new_ethnicity_enum.value:
            new_ethnicity_enum = Ethnicitys.THAI  # Ensure different

        data = EthnicityEditSchema(ethnicity=new_ethnicity_enum)
        ethnicity_obj.gh_update(data)  # This calls save if changed

        expecrted_history_count = 2
        assert ethnicity_obj.history.count() == expecrted_history_count
        latest_history = ethnicity_obj.history.first()  # Most recent
        assert latest_history.history_type == "~"
        assert latest_history.ethnicity == new_ethnicity_enum.value
        assert ethnicity_obj.history.last().history_type == "+"  # Oldest
