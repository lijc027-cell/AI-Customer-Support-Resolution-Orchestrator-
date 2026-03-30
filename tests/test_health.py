from fastapi.testclient import TestClient

from customer_support_resolution.main import app


def test_health_endpoint_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["error"] is None
    assert payload["data"]["service"] == "customer-support-resolution"
    assert payload["data"]["status"] == "ok"
