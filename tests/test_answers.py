"""Checks that every element combination the website allows has stored answers from both models."""
import itertools

import pytest

from chemcheck.answers import ANIONS, CATIONS, METALS, all_answers, combination_key


def test_all_220_combinations_present_with_8_answers_each():
    answers = all_answers()
    assert len(answers) == 220
    for c, m, a in itertools.product(CATIONS, METALS, ANIONS):
        entry = answers[f"{c}-{m}-{a}"]
        assert len(entry["original"]) == 8 and len(entry["dpo"]) == 8
        assert entry["split"] in ("training", "held-out")


def test_44_combinations_are_held_out():
    assert sum(e["split"] == "held-out" for e in all_answers().values()) == 44


def test_combination_key_puts_elements_in_order():
    assert combination_key(["F", "Na", "Mn"]) == "Na-Mn-F"


@pytest.mark.parametrize("bad", [["Na", "K", "F"], ["Na", "Mn", "Fe"], ["Na", "Mn", "Cl"]])
def test_combination_key_rejects_invalid_choices(bad):
    with pytest.raises(ValueError):
        combination_key(bad)