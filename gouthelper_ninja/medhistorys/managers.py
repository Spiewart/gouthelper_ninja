from typing import TYPE_CHECKING

from django.db.models import Manager

from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.medhistorys.schema import MedHistoryEditSchema

if TYPE_CHECKING:
    from uuid import UUID


class AnginaManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.ANGINA)

    def create(self, **kwargs):
        """Create a new Angina record."""
        kwargs.update(
            {
                "mhtype": MHTypes.ANGINA,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class AnticoagulationManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.ANTICOAGULATION)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.ANTICOAGULATION,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class BleedManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.BLEED)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.BLEED,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class CadManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.CAD)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.CAD,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class ChfManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.CHF)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.CHF,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class CkdManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.CKD)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.CKD,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class ColchicineinteractionManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.COLCHICINEINTERACTION)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.COLCHICINEINTERACTION,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class DiabetesManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.DIABETES)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.DIABETES,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class ErosionsManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.EROSIONS)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.EROSIONS,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class GastricbypassManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.GASTRICBYPASS)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.GASTRICBYPASS,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class GoutManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.GOUT)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.GOUT,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class HeartattackManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.HEARTATTACK)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.HEARTATTACK,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class HepatitisManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.HEPATITIS)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.HEPATITIS,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class HypertensionManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.HYPERTENSION)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.HYPERTENSION,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class HyperuricemiaManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.HYPERURICEMIA)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.HYPERURICEMIA,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class IbdManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.IBD)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.IBD,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class MenopauseManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.MENOPAUSE)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.MENOPAUSE,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class OrgantransplantManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.ORGANTRANSPLANT)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.ORGANTRANSPLANT,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class OsteoporosisManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.OSTEOPOROSIS)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.OSTEOPOROSIS,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class PudManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.PUD)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.PUD,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class PadManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.PAD)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.PAD,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class StrokeManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.STROKE)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.STROKE,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class TophiManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.TOPHI)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.TOPHI,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class UratestonesManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.URATESTONES)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.URATESTONES,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)


class XoiinteractionManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.XOIINTERACTION)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.XOIINTERACTION,
            },
        )
        return super().create(**kwargs)

    def gh_create(self, data: MedHistoryEditSchema, patient_id: "UUID"):
        return self.create(**data.dict(), patient_id=patient_id)
