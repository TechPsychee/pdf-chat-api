import pytest
from fastapi.testclient import TestClient


def test_chat_without_pdf(client):
    """Test chat endpoint without uploading PDF first"""
    response = client.post(
        "/v1/chat/invalid_id",
        json={"message": "test message"},
        headers={"X-API-Key": "my-secure-api-key"},
    )
    assert response.status_code == 404


def test_chat_invalid_message(client):
    """Test chat endpoint with invalid message"""
    response = client.post(
        "/v1/chat/some_id",
        json={"message": ""},
        headers={"X-API-Key": "my-secure-api-key"},
    )
    assert response.status_code == 422
