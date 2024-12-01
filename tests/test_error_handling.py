import pytest


def test_file_too_large(client):
    """Test uploading file exceeding size limit"""
    large_content = b"0" * (11 * 1024 * 1024)  # 11MB
    response = client.post(
        "/v1/pdf",
        files={"file": ("large.pdf", large_content, "application/pdf")},
        headers={"X-API-Key": "my-secure-api-key"},
    )
    assert response.status_code == 400


def test_invalid_file_type(client):
    """Test uploading non-PDF file"""
    response = client.post(
        "/v1/pdf",
        files={"file": ("test.txt", b"text content", "text/plain")},
        headers={"X-API-Key": "my-secure-api-key"},
    )
    assert response.status_code == 400


def test_missing_file(client):
    """Test upload endpoint without file"""
    response = client.post("/v1/pdf", headers={"X-API-Key": "my-secure-api-key"})
    assert response.status_code == 422
