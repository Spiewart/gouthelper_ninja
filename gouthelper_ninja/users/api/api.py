from uuid import UUID

from ninja import Router
from ninja.errors import AuthorizationError
from ninja.errors import HttpError
from ninja.security import django_auth

from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.models import User
from gouthelper_ninja.users.querysets import patient_qs
from gouthelper_ninja.users.rules import add_provider_patient
from gouthelper_ninja.users.rules import view_patient
from gouthelper_ninja.users.schema import PatientCreateSchema
from gouthelper_ninja.users.schema import PatientSchema
from gouthelper_ninja.users.schema import ProviderPatientCreateSchema

router = Router()


@router.get("/patients", response=list[PatientSchema], auth=[django_auth])
def get_patients(request):
    return Patient.objects.all()


@router.post("/patients/create", response=PatientSchema)
def create_patient(request, data: PatientCreateSchema) -> Patient:
    return Patient.objects.create(**data.dict())


@router.post("/patients/provider-create/", response=PatientSchema, auth=django_auth)
def create_provider_patient(request, data: ProviderPatientCreateSchema) -> Patient:
    """
    Create a patient with an associated provider.
    """
    if not User.objects.filter(id=data.provider_id).exists():
        raise HttpError(404, f"Provider with id: {data.provider_id} not found.")
    if not add_provider_patient(request.user, data.provider_id):
        msg = (
            f"{request.user} does not have permission to create a "
            "patient for this provider."
        )
        raise AuthorizationError(
            403,
            msg,
        )
    return Patient.objects.create(**data.dict())


@router.get("/patients/{uuid:patient_id}", response={200: PatientSchema})
def get_patient(request, patient_id: UUID) -> Patient:
    try:
        patient = patient_qs(Patient.objects.filter(id=patient_id)).get()
    except Patient.DoesNotExist as e:
        raise HttpError(404, f"Patient with id: {patient_id} not found") from e
    if not view_patient(request.user, patient):
        raise AuthorizationError(
            403,
            f"{request.user} does not have permission to view this patient.",
        )
    return patient


@router.post("/patients/update/{str:patient_id}", response=PatientSchema)
def update_patient(request, patient_id: str, data: PatientSchema) -> Patient:
    patient: Patient = patient_qs(Patient.objects.filter(id=patient_id)).get()
    if not patient:
        raise HttpError(404, f"Patient with ID {patient_id} does not exist.")
    patient.update(**data.dict())
    return patient
