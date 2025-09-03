from ninja import Schema

from gouthelper_ninja.medhistorys.schema import CkdEditSchema
from gouthelper_ninja.medhistorys.schema import MedHistoryEditSchema
from gouthelper_ninja.ults.choices import FlareFreqs
from gouthelper_ninja.ults.choices import FlareNums
from gouthelper_ninja.utils.schema import PatientIdSchema


class UltEditSchema(Schema):
    freq_flares: FlareFreqs
    num_flares: FlareNums
    ckd: CkdEditSchema
    erosions: MedHistoryEditSchema
    hyperuricemia: MedHistoryEditSchema
    tophi: MedHistoryEditSchema
    uratestones: MedHistoryEditSchema


class UltSchema(UltEditSchema, PatientIdSchema):
    """Schema for a Ult."""
