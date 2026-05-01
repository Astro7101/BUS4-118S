from fastapi.testclient import TestClient

from src.api.app import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_support_endpoint() -> None:
    response = client.post(
        "/support",
        json={"user_id": "jdoe", "message": "My VPN keeps disconnecting this morning"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "vpn_issue"
    assert "escalated" in body["response"].lower()
