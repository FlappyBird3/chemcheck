"""Tests for chemcheck.check_answer, using answers whose correct verdicts are known."""
import pytest

from chemcheck import check_answer, extract_formula

REQ = ["Li", "Mn", "O"]
GOOD = "Li: +1, Mn: +4, O: -2\nCheck: 2(+1) + (+4) + 3(-2) = 0\nFormula: Li2MnO3"


def test_balanced_with_supporting_reasoning():
    r = check_answer(GOOD, REQ)
    assert r.score == 1
    assert r.reasoning_supports_formula is True
    assert r.stated_charge_sum == pytest.approx(0)


def test_balanced_with_unsupported_reasoning():
    r = check_answer(GOOD.replace("Mn: +4", "Mn: +2"), REQ)
    assert r.score == 1
    assert r.reasoning_supports_formula is False
    assert r.stated_charge_sum == pytest.approx(-2)


def test_real_unsupported_answer_from_dpo_model():
    r = check_answer("Na: +1, Mn: +7, F: -1\nFormula: NaMnF4", ["Na", "Mn", "F"])
    assert r.balancing_states["Mn"] == pytest.approx(3)
    assert r.stated_charge_sum == pytest.approx(4)


def test_valid_but_unbalanced():
    r = check_answer("Formula: LiMnO5", REQ)
    assert (r.valid, r.balanced, r.score) == (True, False, 0)


def test_wrong_elements_score_minus_one():
    r = check_answer("Formula: H2O", REQ)
    assert r.elements_match is False
    assert r.score == -1


def test_no_formula_line():
    r = check_answer("Li2MnO3 is a nice compound", REQ)
    assert r.formula is None and r.score == -1


def test_missing_stated_state_is_flagged():
    r = check_answer("Na: +1, F: -1\nFormula: NaMnF4", ["Na", "Mn", "F"])
    assert r.reasoning_supports_formula is False
    assert any("Mn" in s for s in r.explanation)


def test_no_required_elements_given():
    r = check_answer("Formula: NaCl")
    assert r.elements_match is None and r.score == 1


@pytest.mark.parametrize("text", ["**Formula:** Li2MnO3", "Formula: Li₂MnO₃", "formula: Li2MnO3."])
def test_formula_formats(text):
    assert extract_formula(text) == "Li2MnO3"