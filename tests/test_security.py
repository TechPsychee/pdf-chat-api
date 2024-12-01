import pytest
import time


def test_api_key_required(client, test_pdf_content):
    """Test that API key is required"""
    response = client.post(
        "/v1/pdf", files={"file": ("test.pdf", test_pdf_content, "application/pdf")}
    )
    assert response.status_code == 403


def test_invalid_api_key(client, test_pdf_content):
    """Test invalid API key"""
    response = client.post(
        "/v1/pdf",
        files={"file": ("test.pdf", test_pdf_content, "application/pdf")},
        headers={"X-API-Key": "invalid-key"},
    )
    assert response.status_code == 403


def test_rate_limiting(client, test_pdf_content):
    """Test rate limiting"""
    headers = {"X-API-Key": "my-secure-api-key"}
    responses = []

    # Make multiple requests quickly
    for _ in range(61):  # Over the limit of 60 per minute
        response = client.post(
            "/v1/pdf",
            files={"file": ("test.pdf", test_pdf_content, "application/pdf")},
            headers=headers,
        )
        responses.append(response.status_code)

    assert 429 in responses  # Should hit rate limit
