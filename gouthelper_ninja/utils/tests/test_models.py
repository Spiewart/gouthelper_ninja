import uuid
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from pydantic import BaseModel as Schema

from gouthelper_ninja.utils.models import GetStrAttrsMixin
from gouthelper_ninja.utils.models import GoutHelperModel


# Define Pydantic Schemas first
class DummyRelatedSchema(Schema):
    name: str


class DummySchema(Schema):
    name: str
    value: int
    related_model: DummyRelatedSchema | None = None


# Define Django Models
class DummyRelatedModel(GoutHelperModel):
    name = models.CharField(max_length=255)

    # This is required by GoutHelperModel.gh_update()
    edit_schema = DummyRelatedSchema

    def gh_update(self, data: DummyRelatedSchema):
        # Simulate update logic for related model
        if self.name != data.name:
            self.name = data.name
            self.save_needed = True
        if self.save_needed:
            self.save()
        return self

    class Meta:
        app_label = "utils"  # Required for dummy models in tests


class DummyModel(GoutHelperModel):
    name = models.CharField(max_length=255)
    value = models.IntegerField(default=0)
    related_model = models.ForeignKey(
        DummyRelatedModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # This is required for testing the update method with a schema
    edit_schema = DummySchema

    class Meta:
        app_label = "utils"  # Required for dummy models in tests


pytestmark = pytest.mark.django_db


class TestGoutHelperModel(TestCase):
    def test_id_field(self):
        obj = DummyModel.objects.create(name="Test", value=1)
        assert isinstance(obj.id, uuid.UUID)

    def test_save_needed_flag_reset_on_save(self):
        obj = DummyModel(name="Test", value=1)
        obj.save_needed = True
        obj.save()
        assert obj.save_needed is False

    def test_delete_needed_flag_reset_on_delete(self):
        obj = DummyModel.objects.create(name="Test", value=1)
        obj.delete_needed = True
        obj.delete()
        assert obj.delete_needed is False

    def test_update_simple_field_changed(self):
        obj = DummyModel.objects.create(name="Old Name", value=10)

        new_data = DummySchema(name="New Name", value=20)
        updated_obj = obj.gh_update(data=new_data)

        assert updated_obj.name == "New Name"
        assert updated_obj.value == new_data.value
        assert updated_obj.save_needed is False  # Should be reset after save
        # Verify it's saved to DB
        obj.refresh_from_db()
        assert obj.name == "New Name"
        assert obj.value == new_data.value

    def test_update_simple_field_not_changed(self):
        obj = DummyModel.objects.create(name="Same Name", value=10)

        new_data = DummySchema(name="Same Name", value=10)
        # Patch save to ensure it's not called if no changes
        with patch.object(obj, "save") as mock_save:
            updated_obj = obj.gh_update(data=new_data)
            mock_save.assert_not_called()

        assert updated_obj.name == "Same Name"
        assert updated_obj.value == new_data.value
        assert updated_obj.save_needed is False  # Should remain False if no changes

    def test_update_related_model_field(self):
        related_obj = DummyRelatedModel.objects.create(name="Related Old")
        obj = DummyModel.objects.create(name="Main", value=1, related_model=related_obj)

        new_related_data = DummyRelatedSchema(name="Related New")
        new_data = DummySchema(
            name="Main Updated",
            value=2,
            related_model=new_related_data,
        )

        # Patch the related model's update method to verify it's called
        with patch.object(
            related_obj,
            "gh_update",
            wraps=related_obj.gh_update,
        ) as mock_related_update:
            updated_obj = obj.gh_update(data=new_data)
            mock_related_update.assert_called_once_with(data=new_related_data)

        assert updated_obj.name == "Main Updated"
        assert updated_obj.value == new_data.value
        assert updated_obj.related_model.name == "Related New"
        assert updated_obj.save_needed is False

        # Verify changes in DB
        obj.refresh_from_db()
        related_obj.refresh_from_db()
        assert obj.name == "Main Updated"
        assert obj.value == new_data.value
        assert related_obj.name == "Related New"

    # https://docs.pytest.org/en/stable/reference/reference.html#:~:text=pytest.mark.filterwarnings
    @pytest.mark.filterwarnings(
        "ignore:.*Pydantic serializer warning.*:UserWarning",
    )
    def test_update_calls_full_clean_before_save(self):
        obj = DummyModel.objects.create(name="Valid", value=1)

        new_data = DummySchema(name="Name is just right", value=2)
        new_data.value = "But value is not valid int"
        with pytest.raises(ValidationError):
            obj.gh_update(data=new_data)

    def test_update_with_none_related_model_remains_none(self):
        obj = DummyModel.objects.create(name="Main", value=1, related_model=None)

        # Update with new simple fields, related_model remains None
        new_data = DummySchema(name="Main Updated", value=2, related_model=None)
        updated_obj = obj.gh_update(data=new_data)

        assert updated_obj.name == "Main Updated"
        assert updated_obj.value == new_data.value
        assert updated_obj.related_model is None
        assert updated_obj.save_needed is False

        obj.refresh_from_db()
        assert obj.name == "Main Updated"
        assert obj.value == new_data.value
        assert obj.related_model is None

    def test_update_assigning_schema_to_none_foreignkey_raises_error(self):
        obj = DummyModel.objects.create(name="Main", value=1, related_model=None)
        new_related_data = DummyRelatedSchema(name="New Related")
        new_data = DummySchema(
            name="Main Updated",
            value=2,
            related_model=new_related_data,
        )

        # This will fail because `setattr(self, 'related_model', new_related_data)`
        # is not a valid assignment for a ForeignKey field.
        with pytest.raises(ValueError, match="Cannot assign"):
            obj.gh_update(data=new_data)


class TestGetStrAttrsMixin(TestCase):
    def test_get_str_attrs_success(self):
        class MyClass(GetStrAttrsMixin):
            def __init__(self):
                self.str_attrs = {
                    "key1": "value1",
                    "key2": "value2",
                    "key3": "value3",
                }

        instance = MyClass()
        result = instance.get_str_attrs("key1", "key3")
        assert result == ("value1", "value3")

    def test_get_str_attrs_missing_key_raises_keyerror(self):
        class MyClass(GetStrAttrsMixin):
            def __init__(self):
                self.str_attrs = {
                    "key1": "value1",
                }

        instance = MyClass()
        with pytest.raises(KeyError):
            instance.get_str_attrs("key_nonexistent")

    def test_get_str_attrs_empty_str_attrs_with_args_raises_keyerror(self):
        class MyClass(GetStrAttrsMixin):
            def __init__(self):
                self.str_attrs = {}

        instance = MyClass()
        with pytest.raises(KeyError):
            instance.get_str_attrs("key1")

    def test_get_str_attrs_empty_str_attrs_no_args_returns_empty_tuple(self):
        class MyClass(GetStrAttrsMixin):
            def __init__(self):
                self.str_attrs = {}

        instance = MyClass()
        result = instance.get_str_attrs()
        assert result == ()
