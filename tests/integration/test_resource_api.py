import pytest


pytestmark = pytest.mark.integration


def test_create_and_list_service(test_client):
    create_response = test_client.post(
        "/services",
        json={
            "name": "opsledger-api",
            "owner_team": "platform",
            "tier": "internal",
            "description": "Primary API service for OpsLedger.",
        },
    )

    assert create_response.status_code == 201
    created_payload = create_response.json()
    assert created_payload["id"] == 1
    assert created_payload["name"] == "opsledger-api"

    list_response = test_client.get("/services")
    assert list_response.status_code == 200
    list_payload = list_response.json()

    assert list_payload["total"] == 1
    assert list_payload["source"] == "database"
    assert list_payload["items"][0]["name"] == "opsledger-api"


def test_create_related_resources_and_validate_readiness(test_client):
    service_response = test_client.post(
        "/services",
        json={
            "name": "opsledger-api",
            "owner_team": "platform",
            "tier": "internal",
            "description": "Primary API service for OpsLedger.",
        },
    )
    assert service_response.status_code == 201
    service_id = service_response.json()["id"]

    deployment_response = test_client.post(
        "/deployments",
        json={
            "service_id": service_id,
            "version": "0.1.0",
            "environment": "test",
            "status": "planned",
        },
    )
    assert deployment_response.status_code == 201

    incident_response = test_client.post(
        "/incidents",
        json={
            "service_id": service_id,
            "severity": "low",
            "status": "open",
            "summary": "Sample test incident.",
        },
    )
    assert incident_response.status_code == 201

    deployments_response = test_client.get("/deployments")
    incidents_response = test_client.get("/incidents")
    readiness_response = test_client.get("/health/ready")

    assert deployments_response.status_code == 200
    assert incidents_response.status_code == 200
    assert readiness_response.status_code == 200

    assert deployments_response.json()["total"] == 1
    assert incidents_response.json()["total"] == 1
    assert readiness_response.json()["checks"]["database"] == "ok"
