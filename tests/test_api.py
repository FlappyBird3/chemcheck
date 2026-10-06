"""Tests for the ChemCheck web API, run without starting a real server."""
from fastapi.testclient import TestClient

from chemcheck.api import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_check_returns_full_result():
    resp = client.post("/check", json={"text": "Na: +1, Mn: +7, F: -1\nFormula: NaMnF4",
                                       "elements": ["Na", "Mn", "F"]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["score"] == 1
    assert body["reasoning_supports_formula"] is False


def test_rejects_request_without_text():
    assert client.post("/check", json={}).status_code == 422


def test_ask_returns_both_models_with_checks():
    resp = client.post("/ask", json={"elements": ["F", "Na", "Mn"], "sample": 0})
    assert resp.status_code == 200
    body = resp.json()
    assert body["combination"] == "Na-Mn-F"
    for model in ("original", "dpo"):
        assert body[model]["verdict"] in ("correct_supported", "correct_unsupported", "incorrect")
        assert "explanation" in body[model]["check"]


def test_ask_rejects_invalid_combination():
    assert client.post("/ask", json={"elements": ["Na", "K", "F"]}).status_code == 400