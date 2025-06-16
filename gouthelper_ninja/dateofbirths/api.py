from ninja import Form
from ninja import Router

from gouthelper_ninja.dateofbirths.models import DateOfBirth
from gouthelper_ninja.dateofbirths.schema import DateOfBirthNestedSchema
from gouthelper_ninja.dateofbirths.schema import DateOfBirthSchema
from gouthelper_ninja.users.querysets import patient_patientprofile_provider_qs

router = Router()


@router.post("/dateofbirths/update/{dateofbirth_id}", response=DateOfBirthSchema)
def update_dateofbirth(
    request,
    dateofbirth_id: str,
    data: DateOfBirthNestedSchema | Form[DateOfBirthNestedSchema],
) -> DateOfBirth:
    dob: DateOfBirth = patient_patientprofile_provider_qs(
        DateOfBirth.objects.filter(id=dateofbirth_id),
    ).get()
    dob.update(**data.dict())
    return dob
