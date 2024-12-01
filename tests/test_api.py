import pytest
from fastapi.testclient import TestClient
import os


def test_root_endpoint(client, api_key_headers):
    """Test the root endpoint"""
    response = client.get("/", headers=api_key_headers)
    assert response.status_code == 200
    assert "message" in response.json()


def test_openapi_docs(client):
    """Test the OpenAPI documentation endpoint"""
    response = client.get("/v1/docs")
    assert response.status_code == 200


def test_invalid_endpoint(client, api_key_headers):
    """Test accessing an invalid endpoint"""
    response = client.get("/invalid", headers=api_key_headers)
    assert response.status_code == 404


def test_environment_variables():
    """Test that required environment variables are set"""
    assert os.getenv("GEMINI_API_KEY") is not None
    assert os.getenv("API_KEY") is not None
