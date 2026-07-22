from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_ask_endpoint_is_grounded():
    response = client.post(
        "/api/cases/GF-2026-014/ask",
        json={"question": "Welche Frist gilt für den Verwendungsnachweis?"}
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["grounded"] is True
    assert payload["citations"]

def test_intake_endpoint():
    response = client.post("/api/cases/GF-2026-014/intake")
    assert response.status_code == 200
    assert response.json()["quarantined"] == 1

def test_phase_one_endpoint():
    response = client.get("/api/phase-one")
    assert response.status_code == 200
    assert len(response.json()) >= 5
