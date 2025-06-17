from uuid import UUID

from ninja import Form
from ninja import Router

from gouthelper_ninja.dateofbirths.models import DateOfBirth
from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.dateofbirths.schema import DateOfBirthSchema
from gouthelper_ninja.users.querysets import patient_patientprofile_provider_qs

router = Router()


@router.post("/dateofbirths/update/{uuid:dateofbirth_id}", response=DateOfBirthSchema)
def update_dateofbirth(
    request,
    dateofbirth_id: UUID,
    data: DateOfBirthEditSchema | Form[DateOfBirthEditSchema],
) -> DateOfBirth:
    dob: DateOfBirth = patient_patientprofile_provider_qs(
        DateOfBirth.objects.filter(id=dateofbirth_id),
    ).get()
    dob.update(data=data)
    return dob
