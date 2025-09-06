from gouthelper_ninja.medhistorys.choices import MHTypes
from gouthelper_ninja.utils.managers import GoutHelperManager


class AnginaManager(GoutHelperManager):
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


class AnticoagulationManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.ANTICOAGULATION)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.ANTICOAGULATION,
            },
        )
        return super().create(**kwargs)


class BleedManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.BLEED)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.BLEED,
            },
        )
        return super().create(**kwargs)


class CadManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.CAD)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.CAD,
            },
        )
        return super().create(**kwargs)


class ChfManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.CHF)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.CHF,
            },
        )
        return super().create(**kwargs)


class CkdManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.CKD)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.CKD,
            },
        )
        return super().create(**kwargs)


class ColchicineinteractionManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.COLCHICINEINTERACTION)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.COLCHICINEINTERACTION,
            },
        )
        return super().create(**kwargs)


class DiabetesManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.DIABETES)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.DIABETES,
            },
        )
        return super().create(**kwargs)


class ErosionsManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.EROSIONS)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.EROSIONS,
            },
        )
        return super().create(**kwargs)


class GastricbypassManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.GASTRICBYPASS)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.GASTRICBYPASS,
            },
        )
        return super().create(**kwargs)


class GoutManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.GOUT)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.GOUT,
            },
        )
        return super().create(**kwargs)


class HeartattackManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.HEARTATTACK)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.HEARTATTACK,
            },
        )
        return super().create(**kwargs)


class HepatitisManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.HEPATITIS)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.HEPATITIS,
            },
        )
        return super().create(**kwargs)


class HypertensionManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.HYPERTENSION)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.HYPERTENSION,
            },
        )
        return super().create(**kwargs)


class HyperuricemiaManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.HYPERURICEMIA)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.HYPERURICEMIA,
            },
        )
        return super().create(**kwargs)


class IbdManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.IBD)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.IBD,
            },
        )
        return super().create(**kwargs)


class MenopauseManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.MENOPAUSE)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.MENOPAUSE,
            },
        )
        return super().create(**kwargs)


class OrgantransplantManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.ORGANTRANSPLANT)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.ORGANTRANSPLANT,
            },
        )
        return super().create(**kwargs)


class OsteoporosisManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.OSTEOPOROSIS)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.OSTEOPOROSIS,
            },
        )
        return super().create(**kwargs)


class PudManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.PUD)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.PUD,
            },
        )
        return super().create(**kwargs)


class PadManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.PAD)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.PAD,
            },
        )
        return super().create(**kwargs)


class StrokeManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.STROKE)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.STROKE,
            },
        )
        return super().create(**kwargs)


class TophiManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.TOPHI)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.TOPHI,
            },
        )
        return super().create(**kwargs)


class UratestonesManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.URATESTONES)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.URATESTONES,
            },
        )
        return super().create(**kwargs)


class XoiinteractionManager(GoutHelperManager):
    def get_queryset(self):
        return super().get_queryset().filter(mhtype=MHTypes.XOIINTERACTION)

    def create(self, **kwargs):
        kwargs.update(
            {
                "mhtype": MHTypes.XOIINTERACTION,
            },
        )
        return super().create(**kwargs)
