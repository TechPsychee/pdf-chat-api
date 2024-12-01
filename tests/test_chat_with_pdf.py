import pytest


def test_chat_flow(client, test_pdf_content):
    """Test complete chat flow with PDF upload"""
    # First upload PDF
    upload_response = client.post(
        "/v1/pdf",
        files={"file": ("test.pdf", test_pdf_content, "application/pdf")},
        headers={"X-API-Key": "my-secure-api-key"},
    )
    assert upload_response.status_code == 200
    pdf_id = upload_response.json()["pdf_id"]

    # Then test chat
    chat_response = client.post(
        f"/v1/chat/{pdf_id}",
        json={"message": "What is this document about?"},
        headers={"X-API-Key": "my-secure-api-key"},
    )
    assert chat_response.status_code == 200
    assert "response" in chat_response.json()
