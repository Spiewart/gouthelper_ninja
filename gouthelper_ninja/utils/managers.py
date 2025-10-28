from typing import TYPE_CHECKING
from typing import Any
from typing import Union

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db.models import ForeignKey
from django.db.models import ForeignObjectRel
from django.db.models import Manager
from django.db.models import ManyToManyField
from django.db.models import OneToOneField
from django.db.models import OneToOneRel

if TYPE_CHECKING:
    from django.db.models import Field
    from django.db.models import Model
    from pydantic import BaseModel as Schema

    from gouthelper_ninja.users.models import Patient
    from gouthelper_ninja.utils.models import GoutHelperCrudMixin


class GoutHelperCRUD:
    def __init__(
        self,
        manager: "GoutHelperManager",
        data: Union["Schema", dict],
        instance: Union["GoutHelperCrudMixin", None] = None,
        patient: Union["Patient", None] = None,
    ):
        self.manager = manager
        self.model = manager.model
        self.data = data.model_dump() if data and not isinstance(data, dict) else data
        self.patient_data = self.get_patient_data()
        self.instance = instance
        self.patient = self.get_or_create_patient(patient)
        self.crud_kwargs = self.get_crud_kwargs()
        self.forward_relations_data = self.get_forward_relations()
        self.reverse_relations_data = self.get_reverse_relations()
        self.m2m_relations_data = self.get_m2m_relations()
        self.forward_relation_kwargs = {}

    def get_crud_kwargs(
        self,
        **kwargs,
    ) -> dict[str, Any]:
        """Get the initial kwargs for creating or updating the model instance.
        This can be overridden in child classes to add additional logic."""
        return {"patient": self.patient, **kwargs}

    def get_patient_data(self) -> dict[str, Any] | None:
        return self.data.pop("patient", None)

    def get_or_create_patient(
        self,
        patient: Union["Patient", None] = None,
    ) -> "Patient":
        if patient:
            if self.patient_data:
                patient.gh_update(
                    self.patient_data,
                )
            return patient

        patient_model: type[Patient] = apps.get_model("users", "Patient")

        if self.patient_data and "id" in self.patient_data:
            patient = patient_model.objects.get(pk=self.patient_data["id"])
            patient.gh_update(self.patient_data)
            return patient

        return patient_model.objects.gh_create(data=self.patient_data)

    def get_forward_relations(
        self,
    ) -> dict[str, tuple["Field", Any]]:
        """Get any forward 1to1 or fields from the data."""
        forward_relations = {}
        for field_name in list(self.data.keys()):
            field = self.get_model_field(field_name)
            if field and isinstance(
                field,
                (ForeignKey, OneToOneField),
            ):
                forward_relations[field_name] = (field, self.data.pop(field_name))
        return forward_relations

    def get_model_field(
        self,
        field_name: str,
    ) -> Union["Field", None]:
        """Check if the field is a OneToOne, ForeignKey, or ManyToMany
        relationship."""
        try:
            field = self.model._meta.get_field(field_name)  # noqa: SLF001
        except FieldDoesNotExist:
            field = None
        return field

    def get_reverse_relations(self) -> dict[str, tuple["Field", Any]]:
        """Get any reverse 1to1 or FK fields from the data."""
        reverse_relations = {}
        for field_name in list(self.data.keys()):
            field = self.get_model_field(field_name)
            if field and isinstance(
                field,
                (ForeignObjectRel, OneToOneRel),
            ):
                reverse_relations[field_name] = (field, self.data.pop(field_name))
        return reverse_relations

    def get_m2m_relations(self) -> dict[str, tuple["Field", Any]]:
        """Get any M2M fields from the data."""
        m2m_relations = {}
        for field_name in list(self.data.keys()):
            field = self.get_model_field(field_name)
            if field and isinstance(field, ManyToManyField):
                m2m_relations[field_name] = (field, self.data.pop(field_name))
        return m2m_relations

    def gh_create(
        self,
    ) -> "Model":
        if self.forward_relations_data:
            for field_name, (field, field_data) in self.forward_relations_data.items():
                self.process_forward_relation(
                    field=field,
                    relation_name=field_name,
                    relation_data=field_data,
                )

        if self.patient_data:
            self.patient.gh_update(self.patient_data)

        self.instance = self.get_or_create_instance(**self.data, **self.crud_kwargs)

        if self.reverse_relations_data:
            for field_name, (field, field_data) in self.reverse_relations_data.items():
                self.process_reverse_relation(
                    field=field,
                    relation_name=field_name,
                    relation_data=field_data,
                )

        if self.m2m_relations_data:
            for field_name, field_data in self.m2m_relations_data.items():
                self.process_m2m_relation(
                    field_name=field_name,
                    field_data=field_data,
                )

        return self.instance

    def process_forward_relation(
        self,
        field: OneToOneField | ForeignKey,
        relation_name: str,
        relation_data: dict[str, Any] | None,
    ) -> None:
        """Process forward relations for OneToOne and ForeignKey fields."""
        if relation_data is not None:
            relation_instance = getattr(
                self.instance,
                relation_name,
                None,
            )
            if relation_instance:
                relation_instance.gh_update(relation_data, **self.crud_kwargs)
            else:
                related_model = field.related_model
                relation_instance = related_model.objects.gh_create(
                    relation_data,
                    **self.crud_kwargs,
                )
                if self.instance:
                    setattr(self.instance, relation_name, relation_instance)
                    self.instance.save_needed = True
            self.forward_relation_kwargs[relation_name] = relation_instance
        else:
            self.process_null_forward_relation(
                relation_name,
            )

    def process_null_forward_relation(
        self,
        relation_name: str,
    ) -> None:
        """Process null forward relations for OneToOne and ForeignKey fields."""
        if self.instance:
            relation_instance = getattr(self.instance, relation_name, None)
            if relation_instance:
                relation_instance.delete()
                setattr(self.instance, relation_name, None)
                self.instance.save_needed = True
        self.forward_relation_kwargs[relation_name] = None

    def get_or_create_instance(self, **kwargs) -> "Model":
        return self.manager.create(**kwargs) if not self.instance else self.instance

    def process_reverse_relation(
        self,
        field: OneToOneRel | ForeignObjectRel,
        relation_name: str,
        relation_data: dict[str, Any] | None,
    ) -> None:
        """Process reverse relations for OneToOne and ForeignKey fields."""
        if relation_data:
            reverse_relation_kwargs = self.update_reverse_relation_kwargs()
            relation_instance = (
                getattr(self.instance, relation_name, None)
                if not self.instance._state.adding  # noqa: SLF001
                else None
            )
            if relation_instance:
                relation_instance.gh_update(
                    relation_data,
                    **reverse_relation_kwargs,
                )
            else:
                related_model = field.related_model
                relation_instance = related_model.objects.gh_create(
                    relation_data,
                    **reverse_relation_kwargs,
                )
        else:
            relation_instance = getattr(self.instance, relation_name, None)
            if relation_instance:
                self.process_null_reverse_relation(
                    relation_instance,
                )

    def update_reverse_relation_kwargs(self) -> dict[str, Any]:
        """Update the reverse relation kwargs with the instance."""
        reverse_relation_kwargs = self.crud_kwargs.copy()
        field_name = self.instance.__class__.__name__.lower()

        field_kwarg = reverse_relation_kwargs.get(field_name, None)
        if not field_kwarg or field_kwarg != self.instance:
            reverse_relation_kwargs[field_name] = self.instance

        return reverse_relation_kwargs

    def process_null_reverse_relation(
        self,
        relation_name: str,
    ) -> None:
        """Process null reverse relations for OneToOne and ForeignKey fields."""
        relation_instance = getattr(self.instance, relation_name, None)
        if relation_instance:
            relation_instance.delete()

    def process_m2m_relation(
        self,
        field_name: str,
        field_data: list[dict[str, Any]] | None,
    ) -> None:
        """Process many-to-many relations for the given field."""
        # TODO: implement M2M processing

    def gh_update(
        self,
    ) -> "GoutHelperCrudMixin":
        if self.forward_relations_data:
            for field_name, (field, field_data) in self.forward_relations_data.items():
                self.process_forward_relation(
                    field=field,
                    relation_name=field_name,
                    relation_data=field_data,
                )

        if self.patient_data:
            self.patient.gh_update(self.patient_data)

        self.update_instance_attrs()

        if self.instance.save_needed:
            self.instance.save()

        if self.reverse_relations_data:
            for field_name, (field, field_data) in self.reverse_relations_data.items():
                self.process_reverse_relation(
                    field=field,
                    relation_name=field_name,
                    relation_data=field_data,
                )

        if self.m2m_relations_data:
            for field_name, field_data in self.m2m_relations_data.items():
                self.process_m2m_relation(
                    field_name=field_name,
                    field_data=field_data[1],
                )

        return self.instance

    def update_instance_attrs(self):
        for key, value in self.data.items():
            if getattr(self.instance, key, None) != value:
                setattr(self.instance, key, value)
                self.instance.save_needed = True

        if self.forward_relation_kwargs:
            for key, value in self.forward_relation_kwargs.items():
                if getattr(self.instance, key, None) != value:
                    setattr(self.instance, key, value)
                    self.instance.save_needed = True
        if self.crud_kwargs:
            for key, value in self.crud_kwargs.items():
                if getattr(self.instance, key, None) != value:
                    setattr(self.instance, key, value)
                    self.instance.save_needed = True


class GoutHelperManager(Manager):
    CRUD_SERVICE = GoutHelperCRUD

    def gh_create(
        self,
        data: Union["Schema", dict],
        patient: Union["Patient", None] = None,
        **kwargs,
    ) -> "Model":
        return self.CRUD_SERVICE(
            manager=self,
            data=data,
            patient=patient,
            **kwargs,
        ).gh_create()

    def gh_update(
        self,
        instance: "GoutHelperCrudMixin",
        data: Union["Schema", dict],
        **kwargs,
    ) -> "GoutHelperCrudMixin":
        return self.CRUD_SERVICE(
            manager=self,
            data=data,
            instance=instance,
            **kwargs,
        ).gh_update()
