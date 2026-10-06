"""Web API for ChemCheck: check any answer, or get both models' stored answers checked by ChemCheck."""
from dataclasses import asdict
from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .answers import all_answers, combination_key
from .checker import CheckResult, check_answer

app = FastAPI(title="ValenceLLM · ChemCheck API", version="0.2.0",
              description="Check AI-generated chemistry answers for charge balance and consistent reasoning.")

# Allow web pages on other addresses (the React site) to call this API. Tightened when deployed.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])


class CheckRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="The answer to check")
    elements: list[str] | None = Field(None, max_length=10,
                                       description="Elements the formula must contain, e.g. ['Na', 'Mn', 'F']")


class AskRequest(BaseModel):
    elements: list[str] = Field(..., min_length=3, max_length=3,
                                description="One main-group metal, one transition metal, and one non-metal")
    sample: int = Field(0, ge=0, le=7, description="Which of each model's 8 stored answers to return")


def verdict(r: CheckResult) -> str:
    """Summarize a check as one of three outcomes for the website to display."""
    if r.score != 1:
        return "incorrect"
    return "correct_supported" if r.reasoning_supports_formula else "correct_unsupported"


@lru_cache(maxsize=None)
def checked_answers(key: str, sample: int) -> dict:
    """Run ChemCheck on both models' answers for one combination, remembering the result."""
    entry, elements = all_answers()[key], key.split("-")
    result = {"combination": key, "split": entry["split"], "sample": sample}
    for model in ("original", "dpo"):
        text = entry[model][sample]
        r = check_answer(text, elements)
        result[model] = {"answer": text, "verdict": verdict(r), "check": asdict(r)}
    return result


@app.get("/")
def root():
    return {"service": "ChemCheck", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/check")
def check(req: CheckRequest):
    return asdict(check_answer(req.text, req.elements))


@app.post("/ask")
def ask(req: AskRequest):
    try:
        key = combination_key(req.elements)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if key not in all_answers():
        raise HTTPException(status_code=404, detail=f"No stored answers for {key}.")
    return checked_answers(key, req.sample)