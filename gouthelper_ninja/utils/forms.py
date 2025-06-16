from typing import TYPE_CHECKING
from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms.layout import Div
from crispy_forms.layout import Fieldset
from crispy_forms.layout import Layout
from django.forms import Form
from django.utils.text import format_lazy

from gouthelper_ninja.utils.helpers import is_iterable
from gouthelper_ninja.utils.models import GetStrAttrsMixin

if TYPE_CHECKING:
    from django.db.models import Model


class GoutHelperForm(Form, GetStrAttrsMixin):
    """Base Form implementation for GoutHelper and its models. Implements
    methods for inserting extra forms into the layout, which is useful for
    nested forms.

    required kwargs:
        patient (Patient): The patient for whom the form is being created.
        request_user (User): The user who is making the request.
        str_attrs (tuple[str]): A tuple of strings that will be used
            as text in the HTML UI.
    optional kwargs:
        sub-form (bool): If True, the form will be rendered as a sub-form
            with a specific CSS class.
    """

    model: type["Model"]

    def __init__(self, *args, **kwargs):
        self.patient = kwargs.pop("patient")
        self.request_user = kwargs.pop("request_user")
        self.str_attrs = kwargs.pop("str_attrs")
        self.sub_form = kwargs.pop("sub-form", False)
        self.fieldset_div_kwargs = {"css_class": "sub-form"} if self.sub_form else {}
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "",
            ),
        )

    @staticmethod
    def default_extra_form_div(
        form_model: str,
    ) -> "Div":
        """Default HTML for extra forms."""

        return Div(
            Div(
                HTML(
                    format_lazy(
                        """\n{}\n{}""",
                        "{% load crispy_forms_tags %}",
                        f"{{% crispy {form_model}_form %}}",
                    ),
                ),
                css_class="col",
            ),
            css_class="row",
            css_id=f"{form_model}",
        )

    def insert_extra_form_at_index(
        self,
        form_model: str,
        indexes: list[int],
        html: Div | None = None,
    ) -> None:
        """Inserts an extra form into the form's layout at a specific index.
        Args:
            form_model (str): The model name of the form to be inserted.
            indexes (list[int]): A list of indexes that lead to the subsection
                where the form should be inserted.
            html (Div | None): The HTML to be inserted. If None, will use the
                default HTML for the extra form.
        Raises:
            IndexError: If the provided indexes are out of range for the layout.
        """

        html = html or self.default_extra_form_div(form_model)

        try:
            index = self.helper.layout
            for i in indexes:
                index = index[i]
        except IndexError as e:
            error_msg = (
                f"Subsection index {indexes} is out of range for the layout of length "
                f"{len(self.helper.layout)}."
            )
            raise IndexError(error_msg) from e

        index.append(html)

    def insert_extra_form(
        self,
        form_model: str,
        html: Div | None = None,
    ) -> None:
        """Inserts an extra form into the form's layout.
        If html is None, will use the default HTML for the extra form.
        If html is provided, will use that instead.
        """

        self.insert_extra_form_at_index(
            indexes=[len(self.helper.layout) - 1],
            form_model=form_model,
            html=html,
        )

    def insert_extra_form_in_subsection(
        self,
        form_model: str,
        subsection: str,
        html: Div | None = None,
    ) -> None:
        """Inserts an extra form into a subsection of the form's layout that
        has a specific css_id.

        Args:
            form_model (str): The model name of the form to be inserted.
            subsection (str): The css_id of the subsection where the form
                should be inserted.
            html (Div | None): The HTML to be inserted. If None, will use the default
                HTML for the extra form.
        Raises:
            ValueError: If the subsection is not found in the layout.
        """
        indexes = self.get_subsection_indexes(
            elements=self.helper.layout,
            subsection=subsection,
        )
        if indexes is None:
            error_msg = f"Subsection {subsection} not found in layout."
            raise ValueError(error_msg)
        self.insert_extra_form_at_index(
            form_model=form_model,
            indexes=indexes,
            html=html,
        )

    @classmethod
    def get_subsection_indexes(
        cls,
        elements: list[Any],
        subsection: str,
        indexes: list[int] | None = None,
    ) -> list[int] | None:
        """Recursive method that searches all elements of a Crispy Forms layout or
        sub-component, such as a Div or Fieldset, for a subsection with a given css_id.
        If found, returns a list of indexes that lead to the subsection.

        Args:
            elements (list[Any]): The list of elements to search through.
            subsection (str): The css_id of the subsection to find.
            indexes (list[int] | None): The current list of indexes leading
                to the subsection.

        Returns:
            list[int] | None: A list of indexes leading to the subsection if found,
                otherwise None.
        """
        found = False
        indexes = [] if indexes is None else indexes

        for i, element in enumerate(elements):
            if element.css_id == subsection:
                indexes.append(i)
                found = True
                break
            if is_iterable(element):
                sub_indexes = cls.get_subsection_indexes(
                    elements=element,
                    subsection=subsection,
                    indexes=[*indexes, i],
                )
                if sub_indexes is not None:
                    indexes = sub_indexes
                    found = True
                    break

        return indexes if found else None
