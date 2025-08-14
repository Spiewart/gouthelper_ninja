from uuid import UUID

from ninja import Router
from ninja.errors import AuthorizationError
from ninja.errors import HttpError

from gouthelper_ninja.ethnicitys.models import Ethnicity
from gouthelper_ninja.ethnicitys.schema import EthnicityEditSchema
from gouthelper_ninja.ethnicitys.schema import EthnicitySchema
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.users.querysets import patient_patientprofile_provider_qs

router = Router()


@router.post(
    "/ethnicitys/update/{uuid:ethnicity_id}",
    response={
        200: EthnicitySchema,
    },
)
def update_ethnicity(
    request,
    ethnicity_id: UUID,
    data: EthnicityEditSchema,
) -> Ethnicity:
    try:
        ethnicity: Ethnicity = patient_patientprofile_provider_qs(
            Ethnicity.objects.filter(id=ethnicity_id),
        ).get()
    except Ethnicity.DoesNotExist as e:
        raise HttpError(
            status_code=404,
            message=f"Ethnicity with id {ethnicity_id} does not exist.",
        ) from e
    if not change_object(request.user, ethnicity):
        msg = f"{request.user} does not have permission to update this Ethnicity."
        raise AuthorizationError(
            403,
            message=msg,
        )
    ethnicity.gh_update(data=data)
    return ethnicity
