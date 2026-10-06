"""Stored answers from the original and DPO-trained models for every allowed element combination."""
import json
from functools import lru_cache
from importlib.resources import files

CATIONS = ["Li", "Na", "K", "Mg", "Ca"]
METALS = ["Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Nb", "Mo"]
ANIONS = ["O", "S", "F", "N"]


@lru_cache(maxsize=1)
def all_answers() -> dict:
    """Load the answer file once, then reuse it for every request."""
    return json.loads(files("chemcheck").joinpath("data/answers.json").read_text())


def combination_key(elements: list[str]) -> str:
    """Order three chosen elements as metal-transition metal-non-metal, e.g. ['F', 'Na', 'Mn'] -> 'Na-Mn-F'."""
    if len(elements) != 3:
        raise ValueError("Choose exactly three elements.")
    picked = []
    for group in (CATIONS, METALS, ANIONS):
        matches = [e for e in elements if e in group]
        if len(matches) != 1:
            raise ValueError("Choose exactly one main-group metal, one transition metal, and one non-metal.")
        picked.append(matches[0])
    return "-".join(picked)