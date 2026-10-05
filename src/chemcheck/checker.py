"""Check AI-generated chemistry answers for charge balance and consistent reasoning."""
import re
from dataclasses import dataclass, field

from pymatgen.core import Composition

_PLAIN = str.maketrans("₀₁₂₃₄₅₆₇₈₉−", "0123456789-")
_FORMULA = re.compile(r"[Ff]ormula:[\s*`]*([A-Z][A-Za-z0-9()]*)")
_STATED = re.compile(r"\b([A-Z][a-z]?):\s*([+-]?\d+)")


def normalize(text: str) -> str:
    """Replace subscript digits and typographic minus signs with plain characters."""
    return text.translate(_PLAIN)


def extract_formula(text: str) -> str | None:
    """Return the last formula given on a 'Formula:' line, or None if there is none."""
    matches = _FORMULA.findall(normalize(text))
    return matches[-1] if matches else None


def stated_states(text: str) -> dict[str, int]:
    """Return the oxidation states the text declares, e.g. {'Mn': 4} for 'Mn: +4'."""
    return {el: int(v) for el, v in _STATED.findall(normalize(text))}


def _fmt(states: dict) -> str:
    return ", ".join(f"{el} {v:+g}" for el, v in states.items())


@dataclass
class CheckResult:
    """Everything ChemCheck found out about one answer."""
    formula: str | None
    valid: bool
    elements_match: bool | None = None
    balanced: bool = False
    balancing_states: dict[str, float] = field(default_factory=dict)
    stated_states: dict[str, int] = field(default_factory=dict)
    stated_charge_sum: float | None = None
    reasoning_supports_formula: bool | None = None
    score: int = -1
    explanation: list[str] = field(default_factory=list)


def check_answer(text: str, elements: list[str] | None = None) -> CheckResult:
    """Check one answer. If `elements` is given, the formula must use exactly those elements.

    Score: 1 = charge-balanced (with the right elements), 0 = valid but not balanced,
    -1 = no usable formula or wrong elements.
    """
    formula, states = extract_formula(text), stated_states(text)
    if formula is None:
        return CheckResult(None, False, stated_states=states,
                           explanation=["No 'Formula:' line was found."])
    try:
        comp = Composition(formula)
    except Exception:
        return CheckResult(formula, False, stated_states=states,
                           explanation=[f"'{formula}' is not a valid chemical formula."])

    r = CheckResult(formula, True, stated_states=states)
    symbols = {el.symbol for el in comp.elements}
    if elements is not None:
        r.elements_match = symbols == set(elements)
        if not r.elements_match:
            r.explanation.append(f"The formula contains {', '.join(sorted(symbols))}, "
                                 f"but the question asked for {', '.join(sorted(elements))}.")

    guesses = comp.oxi_state_guesses()
    r.balanced = bool(guesses)
    if r.balanced:
        r.balancing_states = dict(guesses[0])
        r.explanation.append(f"Charge-balanced with {_fmt(r.balancing_states)}.")
    else:
        r.explanation.append("Not charge-balanced: no common oxidation states sum to zero.")

    if states:
        missing = symbols - states.keys()
        if missing:
            r.reasoning_supports_formula = False
            r.explanation.append(f"No oxidation state is stated for {', '.join(sorted(missing))}.")
        else:
            r.stated_charge_sum = sum(comp[s] * states[s] for s in symbols)
            r.reasoning_supports_formula = abs(r.stated_charge_sum) < 1e-6
            verdict = "supporting" if r.reasoning_supports_formula else "not supporting"
            r.explanation.append(f"The stated states ({_fmt(states)}) sum to "
                                 f"{r.stated_charge_sum:+g}, {verdict} the formula.")

    if r.elements_match is not False:
        r.score = 1 if r.balanced else 0
    return r