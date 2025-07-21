from ninja import Schema
from pydantic import model_validator

from gouthelper_ninja.dateofbirths.schema import DateOfBirthEditSchema
from gouthelper_ninja.ethnicitys.schema import EthnicityEditSchema
from gouthelper_ninja.genders.schema import GenderEditSchema
from gouthelper_ninja.goutdetails.schema import GoutDetailEditSchema
from gouthelper_ninja.medhistorys.schema import MedHistoryEditSchema
from gouthelper_ninja.utils.helpers import menopause_required
from gouthelper_ninja.utils.schema import IdSchema


class PatientEditSchema(
    Schema,
):
    dateofbirth: DateOfBirthEditSchema
    ethnicity: EthnicityEditSchema
    gender: GenderEditSchema
    gout: MedHistoryEditSchema
    goutdetail: GoutDetailEditSchema
    # Menopause is optional, but will be validated given age and gender
    menopause: MedHistoryEditSchema | None = None

    @model_validator(mode="after")
    def validate_menopause(self):
        if (
            menopause_required(
                self.dateofbirth.dateofbirth,
                self.gender.gender,
            )
            and not self.menopause
        ):
            msg = (
                "For females between ages 40 and 60, we need to know the patient's "
                "menopause status to evaluate their flare."
            )
            raise ValueError(msg)
        return self


class PatientSchema(PatientEditSchema, IdSchema):
    pass
