from ninja import Schema

from gouthelper_ninja.medhistorys.schema import CkdEditSchema
from gouthelper_ninja.medhistorys.schema import MedHistoryEditSchema
from gouthelper_ninja.ults.choices import FlareFreqs
from gouthelper_ninja.ults.choices import FlareNums
from gouthelper_ninja.utils.schema import IdSchema
from gouthelper_ninja.utils.schema import OptionalIdSchema


class PatientUltEditSchema(OptionalIdSchema):
    """Schema for a Patient and his or her related models for
    creating or updating his or her ULT."""

    ckd: CkdEditSchema
    erosions: MedHistoryEditSchema
    hyperuricemia: MedHistoryEditSchema
    tophi: MedHistoryEditSchema
    uratestones: MedHistoryEditSchema


class UltEditSchema(Schema):
    freq_flares: FlareFreqs
    num_flares: FlareNums
    patient: PatientUltEditSchema


class PatientUltSchema(IdSchema, PatientUltEditSchema):
    """Schema for a Patient and his or her related models for
    viewing his or her ULT."""


class UltSchema(IdSchema):
    """Schema for a Ult."""

    patient: PatientUltSchema
