from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms.layout import Div
from crispy_forms.layout import Fieldset
from crispy_forms.layout import Layout
from django.test import TestCase

from gouthelper_ninja.utils.forms import GoutHelperForm


class TestGoutHelperForm(TestCase):
    """Test the GoutHelperForm class."""

    def setUp(self):
        self.form = GoutHelperForm()

    def test__init__(self):
        assert isinstance(self.form, GoutHelperForm)

        assert hasattr(self.form, "patient")
        assert self.form.patient is None

        assert hasattr(self.form, "request_user")
        assert self.form.request_user is None

        assert hasattr(self.form, "str_attrs")
        assert self.form.str_attrs is None

        assert hasattr(self.form, "sub_form")
        assert self.form.sub_form is False

        assert hasattr(self.form, "fieldset_div_kwargs")
        assert isinstance(self.form.fieldset_div_kwargs, dict)

        assert hasattr(self.form, "helper")
        assert isinstance(self.form.helper, FormHelper)

        assert self.form.helper.form_tag is False

        assert isinstance(self.form.helper.layout, Layout)
        assert len(self.form.helper.layout) == 1
        assert isinstance(self.form.helper.layout[0], Fieldset)
        assert self.form.helper.layout[0].legend == ""

    def test__default_extra_form_html(self):
        html = GoutHelperForm.default_extra_form_div("test")

        assert isinstance(html, Div)
        assert html.css_class == "row"
        assert html.css_id == "test"

        assert isinstance(html[0], Div)
        assert html[0].css_class == "col"

        assert isinstance(html[0][0], HTML)

        assert html[0][0].html == (
            "\n{% load crispy_forms_tags %}\n{% crispy test_form %}"
        )

    def test__insert_extra_form(self):
        self.form.insert_extra_form("test")
        assert self.form.helper.layout[0][0].css_id == "test"

    def test__insert_extra_form_at_index(self):
        self.form.insert_extra_form_at_index("test-1", indexes=[0])
        assert self.form.helper.layout[0][0].css_id == "test-1"

    def test__insert_extra_form_subsection(self):
        # Insert a subsection, which will have index [0][0]
        self.form.helper.layout[0].append(
            Div(css_id="test-1"),
        )
        # Insert an extra form in the subsection
        self.form.insert_extra_form_in_subsection("test-2", subsection="test-1")
        assert isinstance(self.form.helper.layout[0][0][0], Div)
        assert self.form.helper.layout[0][0][0].css_id == "test-2"

    def test__get_subsection_indexes(self):
        """Test the get_subsection_indexes method, which recursively
        searches for a subsection with a given css_id attribute in
        Crispy Forms layouts and sub-components. Needs to work even
        for deeply nested structures."""
        # Insert a subsection with css_id "test_id"
        self.form.helper.layout.append(
            Div(css_id="test_id"),
        )
        # Check if the method can find it
        indexes = self.form.get_subsection_indexes(self.form.helper.layout, "test_id")
        assert indexes == [1]
        assert self.form.helper.layout[indexes[0]].css_id == "test_id"

        # Insert a subsection with css_id "test_id2" at index 2
        self.form.helper.layout.append(
            Div(css_id="test_id2"),
        )
        # Check if the method can find it
        indexes = self.form.get_subsection_indexes(self.form.helper.layout, "test_id2")
        assert indexes == [2]
        assert self.form.helper.layout[indexes[0]].css_id == "test_id2"
        # Insert a subsection with css_id "test_id2_subsection" at index 2,0
        self.form.helper.layout[2].append(
            Div(css_id="test_id2_subsection"),
        )
        # Check if the method can find it
        indexes = self.form.get_subsection_indexes(
            self.form.helper.layout,
            "test_id2_subsection",
        )
        assert indexes == [2, 0]
        assert (
            self.form.helper.layout[indexes[0]][indexes[1]].css_id
            == "test_id2_subsection"
        )
        # Insert a subsection with css_id "test_id2_subsection_deep_nest" at index 2,0,0
        # This is a deeply nested subsection
        self.form.helper.layout[2][0].append(
            Div(
                css_id="test_id2_subsection_deep_nest",
            ),
        )
        # Check if the method can find it
        indexes = self.form.get_subsection_indexes(
            self.form.helper.layout,
            "test_id2_subsection_deep_nest",
        )

        assert indexes == [2, 0, 0]
        assert (
            self.form.helper.layout[indexes[0]][indexes[1]][indexes[2]].css_id
            == "test_id2_subsection_deep_nest"
        )
