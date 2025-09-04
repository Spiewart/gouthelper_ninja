from typing import TYPE_CHECKING
from typing import Any
from typing import Union

from django.db.models import Manager
from pydantic import BaseModel as Schema

from gouthelper_ninja.users.models import Patient

if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models import Model


class GoutHelperManager(Manager):
    def gh_create(
        self,
        data: Union["Schema", dict],
        patient: Union[Patient, "UUID"],
    ) -> "Model":
        patient = (
            patient if isinstance(patient, Patient) else Patient.objects.get(pk=patient)
        )
        create_kwargs = {
            "patient": patient,
        }
        if not isinstance(data, dict):
            data = data.model_dump()

        for field_name, field_data in data.items():
            self.process_schema_field(
                field_name=field_name,
                field_data=field_data,
                create_kwargs=create_kwargs,
                patient=patient,
            )
        return self.create(**create_kwargs)

    def process_schema_field(
        self,
        field_name: str,
        field_data: Union["Schema", dict, None],
        create_kwargs: dict[str, Any],
        patient: "Patient",
    ) -> None:
        """Processes a field from a Pydantic Schema and either calls other
        CRUD methods or updates the create_kwargs for the calling Model."""
        if field_data and isinstance(field_data, Schema):
            field_data = field_data.model_dump()

        if self.model.field_is_related_model(field_name):
            if self.model.field_is_onetoone(field_name):
                self.process_onetoone_data(
                    patient=patient,
                    field_name=field_name,
                    field_data=field_data,
                    create_kwargs=create_kwargs,
                )
            else:
                # TODO: Handle ManyToMany relationships
                pass
        elif patient.field_is_related_model(field_name):
            if patient.field_is_onetoone(field_name):
                self.process_onetoone_data(
                    patient=patient,
                    field_name=field_name,
                    field_data=field_data,
                    create_kwargs=create_kwargs,
                )
            else:
                # TODO: Handle ManyToMany relationships
                pass
        elif field_data:
            create_kwargs[field_name] = field_data

    @classmethod
    def process_onetoone_data(
        cls,
        patient: Patient,
        field_name: str,
        field_data: Union["Schema", dict, None],
        create_kwargs: dict[str, Any],
    ) -> None:
        related_model = getattr(patient, field_name).related_model
        if field_data:
            if "id" in field_data:
                related_instance = related_model.objects.get(
                    pk=field_data["id"],
                )
            else:
                related_instance = related_model.gh_create(
                    data=field_data,
                    patient=patient,
                )
            create_kwargs[field_name] = related_instance
