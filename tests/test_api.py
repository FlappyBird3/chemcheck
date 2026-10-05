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