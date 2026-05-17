"""
Integration tests for email API routes.
"""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint_reports_ok(api_client):
    response = await api_client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database"] is True


@pytest.mark.asyncio
async def test_create_get_list_and_process_email(api_client):
    create_payload = {
        "subject": "Integration Test Email",
        "sender": "sender@example.com",
        "recipient": "recipient@example.com",
        "body": "Please summarize this message.",
    }

    create_response = await api_client.post("/api/v1/emails", json=create_payload)
    assert create_response.status_code == 201

    created_email = create_response.json()
    assert created_email["subject"] == create_payload["subject"]
    assert created_email["status"] == "pending"
    assert created_email["logs"] == []

    email_id = created_email["id"]

    get_response = await api_client.get(f"/api/v1/emails/{email_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == email_id

    list_response = await api_client.get("/api/v1/emails")
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert list_payload["total"] == 1
    assert list_payload["size"] == 10
    assert len(list_payload["items"]) == 1

    process_response = await api_client.post(f"/api/v1/emails/{email_id}/process")
    assert process_response.status_code == 200
    processed_email = process_response.json()
    assert processed_email["status"] == "completed"
    assert processed_email["ai_summary"] == "Summary of: Integration Test Email"
    assert len(processed_email["logs"]) == 1
    assert processed_email["logs"][0]["step"] == "ai_analysis"

    filtered_response = await api_client.get("/api/v1/emails", params={"status": "completed"})
    assert filtered_response.status_code == 200
    filtered_payload = filtered_response.json()
    assert filtered_payload["total"] == 1
    assert filtered_payload["items"][0]["status"] == "completed"