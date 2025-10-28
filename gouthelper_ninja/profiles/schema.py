from gouthelper_ninja.utils.schema import IdSchema
from gouthelper_ninja.utils.schema import PatientEditSchema


class PatientProfileEditSchema(PatientEditSchema):
    provider: IdSchema | None
