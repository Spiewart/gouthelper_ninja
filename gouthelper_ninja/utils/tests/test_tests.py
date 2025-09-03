from django.test import TestCase

from gouthelper_ninja.users.tests.factories import PatientFactory


class TestGetters(TestCase):
    def test__hasattr(self):
        patient_with_dob = PatientFactory()
        assert hasattr(patient_with_dob, "dateofbirth")

        patient_without_dob = PatientFactory(dateofbirth=None)
        assert not hasattr(patient_without_dob, "dateofbirth")

        assert hasattr(patient_with_dob, "gout")

        assert hasattr(patient_without_dob, "ckd")
        assert patient_without_dob.ckd is None
