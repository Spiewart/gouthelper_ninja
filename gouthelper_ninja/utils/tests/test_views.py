from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from gouthelper_ninja.utils.views import GoutHelperCreateMixin
from gouthelper_ninja.utils.views import GoutHelperEditMixin
from gouthelper_ninja.utils.views import GoutHelperUpdateMixin
from gouthelper_ninja.utils.views import PatientKwargMixin
from gouthelper_ninja.utils.views import PatientObjectMixin

User = get_user_model()


class DummySchema:
    model_fields = ["foo", "bar"]

    def __init__(self, **kwargs):
        self.data = kwargs


# Define a single FakeModel for both DummyForm and View
class FakeModel:
    pass


class DummyForm:
    model = FakeModel

    def __init__(self, **kwargs):
        self.cleaned_data = kwargs

    def is_valid(self):
        return True


class DummyField:
    def __init__(self, name):
        self.name = name


class DummyModel:
    _meta = MagicMock()
    _meta.get_fields.return_value = [DummyField("foo"), DummyField("bar")]
    foo = "foo_val"
    bar = "bar_val"


@pytest.mark.django_db
def test_get_permission_object_returns_patient():
    class View(GoutHelperEditMixin):
        patient = "patient_obj"

    v = View()
    assert v.get_permission_object() == "patient_obj"


@pytest.mark.django_db
def test_get_form_kwargs_includes_subform_kwargs():
    foo_kwarg = 1
    bar_kwarg = 2

    class View(GoutHelperEditMixin):
        def get_initial(self) -> dict[str, int]:
            return {"foo": foo_kwarg}

        def get_prefix(self) -> str:
            return "prefix"

        request = MagicMock(method="GET")
        subform_kwargs = {"bar": bar_kwarg}

    v = View()
    kwargs = v.get_form_kwargs()

    assert kwargs["initial"] == {"foo": foo_kwarg}
    assert kwargs["prefix"] == "prefix"
    assert kwargs["bar"] == bar_kwarg


@pytest.mark.django_db
def test_get_initial_populates_from_object():
    class Base:
        def get_initial(self):
            return {}

    class View(GoutHelperEditMixin, Base):  # Fix: Mixin first
        object = DummyModel()
        schema = DummySchema

    v = View()
    initial = v.get_initial()
    assert initial["foo"] == "foo_val"
    assert initial["bar"] == "bar_val"


@pytest.mark.django_db
def test_subform_kwargs_property():
    class View(GoutHelperEditMixin):
        patient = "pat"
        request_user = "req_user"
        str_attrs = {"a": "b"}

    v = View()
    assert v.subform_kwargs == {
        "patient": "pat",
        "request_user": "req_user",
        "str_attrs": {"a": "b"},
    }


@pytest.mark.django_db
def test_str_attrs_returns_dict():
    class View(GoutHelperEditMixin):
        patient = None
        request_user = None

    v = View()
    with patch(
        "gouthelper_ninja.utils.views.get_str_attrs_dict",
        return_value={"x": "y"},
    ):
        assert v.str_attrs == {"x": "y"}


@pytest.mark.django_db
def test_request_user_returns_request_user():
    class DummyReq:
        user = "theuser"

    class View(GoutHelperEditMixin):
        request = DummyReq()

    v = View()
    assert v.request_user == "theuser"


@pytest.mark.django_db
def test_patient_kwarg_mixin():
    class DummyPatient:
        objects = MagicMock()
        objects.filter.return_value.get.return_value = "thepatient"

    class View(PatientKwargMixin):
        kwargs = {"patient": 1}
        Patient = DummyPatient

    with patch("gouthelper_ninja.utils.views.Patient", DummyPatient):
        v = View()
        assert v.patient == "thepatient"


@pytest.mark.django_db
def test_patient_object_mixin():
    class DummyObj:
        patient = "thepatient"

    class View(PatientObjectMixin):
        object = DummyObj()

    v = View()
    assert v.patient == "thepatient"


@pytest.mark.django_db
def test_create_mixin_post_sets_object():
    # Ensure FakeModel is the same everywhere
    class View(GoutHelperCreateMixin):
        model = FakeModel
        schema = DummySchema

        def get_form_class(self):
            return DummyForm

        def get_form_kwargs(self):
            return {"foo": "bar"}

        def get_success_url(self):
            return "/success/"

        request = MagicMock(method="POST", POST={}, FILES={}, htmx=False)

        def create_schema(self, data):
            return DummySchema(**data)

        def create_object(self, schema, **kwargs):
            self.created = True
            return "obj"

        def form_valid(self, schema, **kwargs):
            self.valid_called = True
            return super().form_valid(schema, **kwargs)

        def post_forms_valid(self):
            return True

        def post_init(self):
            # Use the same FakeModel for both
            form = DummyForm(foo="bar")
            form.model = FakeModel
            self.forms = {"form": form}

    v = View()
    v.object = None
    v.created = False
    v.valid_called = False
    v.post(v.request)
    assert v.created
    assert v.valid_called


@pytest.mark.django_db
def test_update_mixin_post_sets_object():
    class View(GoutHelperUpdateMixin):
        model = MagicMock()
        schema = DummySchema

        def get_form_class(self):
            return DummyForm

        def get_form_kwargs(self):
            return {"foo": "bar"}

        def get_success_url(self):
            return "/success/"

        request = MagicMock(method="POST", POST={}, FILES={}, htmx=False)

        def create_schema(self, data):
            return DummySchema(**data)

        def get_object(self):
            return MagicMock(update=lambda data: "updated_obj")

        def form_valid(self, schema, **kwargs):
            self.valid_called = True
            return "ok"

        def post_forms_valid(self):
            return True

        def post_init(self):
            self.forms = {"form": DummyForm()}

    v = View()
    v.valid_called = False
    v.post(v.request)
    assert v.valid_called
