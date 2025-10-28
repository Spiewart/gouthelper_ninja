from typing import Any

from django.apps import apps

from gouthelper_ninja.utils.managers import GoutHelperCRUD
from gouthelper_ninja.utils.managers import GoutHelperManager


class PatientProfileCrud(GoutHelperCRUD):
    def get_crud_kwargs(self, **kwargs) -> dict[str, Any]:
        crud_kwargs = super().get_crud_kwargs(**kwargs)
        provider_data = self.data.pop("provider", None)
        provider_id = provider_data.get("id") if provider_data else None
        if provider_id:
            Provider = apps.get_model("users", "Provider")
            provider = Provider.objects.get(id=provider_id)
        else:
            provider = None
        crud_kwargs["provider"] = provider
        return crud_kwargs


class PatientProfileManager(GoutHelperManager):
    CRUD_SERVICE = PatientProfileCrud
