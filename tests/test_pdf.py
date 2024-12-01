import pytest


def test_pdf_upload_success(client, test_pdf_content):
    """Test successful PDF upload"""
    response = client.post(
        "/v1/pdf",
        files={"file": ("test.pdf", test_pdf_content, "application/pdf")},
        headers={"X-API-Key": "my-secure-api-key"},
    )
    assert response.status_code == 200
    assert "pdf_id" in response.json()
    assert "filename" in response.json()
    assert "size" in response.json()


def test_pdf_content_extraction(client, test_pdf_content):
    """Test PDF content extraction"""
    response = client.post(
        "/v1/pdf",
        files={"file": ("test.pdf", test_pdf_content, "application/pdf")},
        headers={"X-API-Key": "my-secure-api-key"},
    )
    assert "text_content" in response.json()
    assert len(response.json()["text_content"]) > 0
