from gouthelper_ninja.ckddetails.choices import DialysisChoices
from gouthelper_ninja.ckddetails.choices import DialysisDurations
from gouthelper_ninja.ckddetails.choices import Stages
from gouthelper_ninja.ckddetails.forms import CkdDetailForm


def _make_form(data: dict | None = None):
    kwargs = {
        "patient": None,
        "request_user": None,
        "str_attrs": {
            "Tobe": "Is",
            "subject_the": "the patient",
            "subject_the_pos": "the patient's",
        },
    }
    if data is not None:
        return CkdDetailForm(data=data, **kwargs)
    return CkdDetailForm(**kwargs)


def test_clean_adds_errors_when_dialysis_true_but_missing_details():
    form = _make_form({"dialysis": "True"})
    assert not form.is_valid()
    # dialysis_type and dialysis_duration should have errors
    assert "dialysis_type" in form.errors
    assert "dialysis_duration" in form.errors


def test_clean_sets_stage_to_five_when_on_dialysis_and_stage_not_five():
    form = _make_form(
        {
            "dialysis": "True",
            "dialysis_type": str(DialysisChoices.HEMODIALYSIS),
            "dialysis_duration": str(DialysisDurations.LESSTHANSIX),
            "stage": str(Stages.THREE),
        },
    )
    assert form.is_valid()
    cleaned = form.clean()
    assert cleaned["stage"] == Stages.FIVE


def test_clean_clears_type_and_duration_when_not_on_dialysis():
    form = _make_form(
        {
            "dialysis": "False",
            "dialysis_type": str(DialysisChoices.HEMODIALYSIS),
            "dialysis_duration": str(DialysisDurations.LESSTHANSIX),
        },
    )
    assert form.is_valid()
    cleaned = form.clean()
    assert cleaned["dialysis_type"] is None
    assert cleaned["dialysis_duration"] is None


def test_help_texts_contain_expected_phrases():
    form = _make_form()
    dialysis_help = str(form.fields["dialysis"].help_text)
    assert "dialysis" in dialysis_help.lower()
    stage_help = str(form.fields["stage"].help_text)
    assert "baseline creatinine" in stage_help.lower()
