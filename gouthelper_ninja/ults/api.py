from uuid import UUID

from ninja import Router
from ninja.errors import AuthorizationError
from ninja.errors import HttpError

from gouthelper_ninja.rules import change_object
from gouthelper_ninja.ults.models import Ult
from gouthelper_ninja.ults.schema import UltEditSchema
from gouthelper_ninja.ults.schema import UltSchema
from gouthelper_ninja.users.querysets import patient_patientprofile_provider_qs

router = Router()


@router.post(
    "/ults/update/{uuid:ult_id}",
    response={
        200: UltSchema,
    },
)
def update_ult(
    request,
    ult_id: UUID,
    data: UltEditSchema,
) -> Ult:
    """API endpoint for updating a Ult object."""
    try:
        ult: Ult = patient_patientprofile_provider_qs(
            Ult.objects.filter(id=ult_id),
        ).get()
    except Ult.DoesNotExist as e:
        raise HttpError(
            status_code=404,
            message=f"Ult with id {ult_id} does not exist.",
        ) from e
    if not change_object(request.user, ult):
        msg = f"{request.user} does not have permission to update this Ult."
        raise AuthorizationError(
            403,
            message=msg,
        )
    ult.gh_update(data=data)
    return ult
