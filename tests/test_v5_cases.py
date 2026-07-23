from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_v5_lists_three_human_readable_cases():
    response = client.get("/api/v5/cases")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 3
    assert {item["id"] for item in items} == {
        "glasfaser-sonnenhain",
        "wohngeld-vollstaendigkeit",
        "vergaberegel-schul-it",
    }
    assert all(item["title"] and item["question"] for item in items)


def test_v5_wohngeld_question_is_grounded_and_human_bounded():
    response = client.post(
        "/api/v5/cases/wohngeld-vollstaendigkeit/ask",
        json={"question": "Welche Unterlagen fehlen und was ist der nächste Schritt?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["grounded"] is True
    assert "Nebenkostennachweis" in data["answer"]
    assert len(data["citations"]) == 2
    assert any(step["tool"] == "human_boundary_check" for step in data["trace"])


def test_v5_gitlaw_bridge_explains_affected_projects():
    response = client.post(
        "/api/v5/cases/vergaberegel-schul-it/ask",
        json={"question": "Welche Projekte sind von der Änderung 2027 betroffen?"},
    )
    assert response.status_code == 200
    assert "Schulcampus Nord" in response.json()["answer"]


def test_v5_page_is_mobile_self_contained():
    response = client.get("/v5")
    assert response.status_code == 200
    assert "Drei Fälle, die Menschen sofort verstehen" in response.text
    assert "@media(max-width:680px)" in response.text
    assert '<link rel="stylesheet"' not in response.text
