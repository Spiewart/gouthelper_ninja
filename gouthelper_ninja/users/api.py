from ninja import Router

from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.querysets import patient_update_qs
from gouthelper_ninja.users.schema import PatientCreateSchema
from gouthelper_ninja.users.schema import PatientSchema
from gouthelper_ninja.users.schema import PatientUpdateSchema

router = Router()


@router.get("/patients/", response=list[PatientSchema])
def get_patients(request):
    return Patient.objects.all()


@router.get("/patients/{patient_id}/", response=PatientSchema)
def get_patient(request, patient_id: str):
    return Patient.objects.get(id=patient_id)


@router.post("/patients/create/", response=PatientSchema)
def create_patient(request, data: PatientCreateSchema):
    return Patient.objects.create(**data.dict())


@router.post("/patients/update/{patient_id}/", response=PatientUpdateSchema)
def update_patient(request, patient_id: str, data: PatientUpdateSchema):
    patient = patient_update_qs(Patient.objects.filter(id=patient_id)).get()
    patient.update(**data.dict())
    return patient
