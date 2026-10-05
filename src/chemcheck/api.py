"""Web API for ChemCheck: send an answer, get back the full check as JSON."""
from dataclasses import asdict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .checker import check_answer

app = FastAPI(title="ChemCheck", version="0.1.0",
              description="Check AI-generated chemistry answers for charge balance and consistent reasoning.")

# Allow web pages on other addresses (the React site) to call this API. Tightened when deployed.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])


class CheckRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="The answer to check")
    elements: list[str] | None = Field(None, max_length=10,
                                       description="Elements the formula must contain, e.g. ['Na', 'Mn', 'F']")


@app.get("/")
def root():
    return {"service": "ChemCheck", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/check")
def check(req: CheckRequest):
    return asdict(check_answer(req.text, req.elements))