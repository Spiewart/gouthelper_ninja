from uuid import UUID

from ninja import Router
from ninja.errors import AuthorizationError
from ninja.errors import HttpError

from gouthelper_ninja.genders.models import Gender
from gouthelper_ninja.genders.schema import GenderEditSchema
from gouthelper_ninja.genders.schema import GenderSchema
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.users.querysets import patient_patientprofile_provider_qs

router = Router()


@router.post(
    "/genders/update/{uuid:gender_id}",
    response={
        200: GenderSchema,
    },
)
def update_gender(
    request,
    gender_id: UUID,
    data: GenderEditSchema,
) -> Gender:
    try:
        gender: Gender = patient_patientprofile_provider_qs(
            Gender.objects.filter(id=gender_id),
        ).get()
    except Gender.DoesNotExist as e:
        raise HttpError(
            status_code=404,
            message=f"Gender with id {gender_id} does not exist.",
        ) from e
    if not change_object(request.user, gender):
        msg = f"{request.user} does not have permission to update this Gender."
        raise AuthorizationError(
            403,
            message=msg,
        )
    gender.gh_update(data=data)
    return gender
