from uuid import UUID

from ninja import Router
from ninja.errors import AuthorizationError
from ninja.errors import HttpError

from gouthelper_ninja.ckddetails.models import CkdDetail
from gouthelper_ninja.ckddetails.schema import CkdDetailEditSchema
from gouthelper_ninja.ckddetails.schema import CkdDetailSchema
from gouthelper_ninja.rules import add_object
from gouthelper_ninja.rules import change_object
from gouthelper_ninja.users.models import Patient
from gouthelper_ninja.users.querysets import patient_patientprofile_provider_qs
from gouthelper_ninja.users.querysets import patient_profile_qs

router = Router()


@router.post(
    "/create/{uuid:patient_id}",
    response={
        200: CkdDetailSchema,
    },
)
def create_ckddetail(
    request,
    patient_id: UUID,
    data: CkdDetailEditSchema,
) -> CkdDetail:
    """
    Create a new CkdDetail for a patient.
    """
    try:
        patient = patient_profile_qs(
            Patient.objects.filter(id=patient_id),
        ).get()
    except Patient.DoesNotExist as e:
        raise HttpError(
            status_code=404,
            message=f"Patient with id {patient_id} does not exist.",
        ) from e
    if not add_object(request.user, patient):
        msg = (
            f"{request.user} does not have permission to create a "
            "CkdDetail for this patient."
        )
        raise AuthorizationError(
            status_code=403,
            message=msg,
        )
    return CkdDetail.objects.gh_create(data=data, patient_id=patient_id)


@router.post(
    "/update/{uuid:ckddetail_id}",
    response={
        200: CkdDetailSchema,
    },
)
def update_ckddetail(
    request,
    ckddetail_id: UUID,
    data: CkdDetailEditSchema,
) -> CkdDetail:
    try:
        ckddetail: CkdDetail = patient_patientprofile_provider_qs(
            CkdDetail.objects.filter(id=ckddetail_id),
        ).get()
    except CkdDetail.DoesNotExist as e:
        raise HttpError(
            status_code=404,
            message=f"CkdDetail with id {ckddetail_id} does not exist.",
        ) from e
    if not change_object(request.user, ckddetail):
        msg = f"{request.user} does not have permission to update this CkdDetail."
        raise AuthorizationError(
            403,
            message=msg,
        )
    ckddetail.gh_update(data=data)
    return ckddetail
