from typing import TYPE_CHECKING

from django.db.models import Manager

from gouthelper_ninja.ckddetails.schema import CkdDetailEditSchema

if TYPE_CHECKING:
    from uuid import UUID


class CkdDetailManager(Manager):
    def gh_create(self, data: CkdDetailEditSchema, patient_id: "UUID"):
        return self.create(**data.model_dump(), patient_id=patient_id)
