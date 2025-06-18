from uuid import UUID

from ninja import Router
from ninja.errors import AuthorizationError
from ninja.errors import HttpError

from gouthelper_ninja.dateofbirths.models import DateOfBirth
from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.dateofbirths.schema import DateOfBirthSchema
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.users.querysets import patient_patientprofile_provider_qs

router = Router()


@router.post(
    "/dateofbirths/update/{uuid:dateofbirth_id}",
    response={
        200: DateOfBirthSchema,
    },
)
def update_dateofbirth(
    request,
    dateofbirth_id: UUID,
    data: DateOfBirthEditSchema,
) -> DateOfBirth:
    try:
        dob: DateOfBirth = patient_patientprofile_provider_qs(
            DateOfBirth.objects.filter(id=dateofbirth_id),
        ).get()
    except DateOfBirth.DoesNotExist as e:
        raise HttpError(
            status_code=404,
            message=f"DateOfBirth with id {dateofbirth_id} does not exist.",
        ) from e
    if not change_object(request.user, dob):
        msg = f"{request.user} does not have permission to update this DateOfBirth."
        raise AuthorizationError(
            403,
            message=msg,
        )
    dob.update(data=data)
    return dob
