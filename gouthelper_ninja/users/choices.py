from django.db.models import IntegerChoices


# User types for different roles
class Roles(IntegerChoices):
    PATIENT = 1, "Patient"
    PROVIDER = 2, "Provider"
    PSEUDOPATIENT = 3, "Pseudopatient"
    ADMIN = 4, "Admin"
