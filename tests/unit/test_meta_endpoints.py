import pytest


pytestmark = pytest.mark.unit


def test_health_live_returns_ok(plain_client):
    response = plain_client.get("/health/live")

    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["checks"]["application"] == "ok"
    assert payload["app_name"] == "opsledger-platform"


def test_version_returns_expected_metadata(plain_client):
    response = plain_client.get("/version")

    assert response.status_code == 200
    payload = response.json()

    assert payload["app_name"] == "opsledger-platform"
    assert payload["app_version"] == "0.1.0"
    assert payload["environment"] == "local"
