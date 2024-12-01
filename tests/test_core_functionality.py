# tests/test_core_functionality.py

import pytest
from fastapi.testclient import TestClient
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from .test_env import TEST_SETTINGS

# Import app after environment setup
from app.main import app

client = TestClient(app)


class TestPDFProcessing:
    """Test Suite for Requirement 1: Efficient PDF uploading and processing"""

    def test_pdf_upload_performance(self, test_pdf_content, api_key_headers):
        """Test upload speed and efficiency"""
        start_time = time.time()
        response = client.post(
            "/v1/pdf",
            files={"file": ("test.pdf", test_pdf_content, "application/pdf")},
            headers=api_key_headers,
        )
        processing_time = time.time() - start_time

        assert response.status_code == 200
        assert processing_time < 2.0  # Upload should complete within 2 seconds
        assert "pdf_id" in response.json()

    def test_concurrent_uploads(self, test_pdf_content, api_key_headers):
        """Test handling multiple concurrent uploads"""
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for _ in range(5):
                futures.append(
                    executor.submit(
                        client.post,
                        "/v1/pdf",
                        files={
                            "file": ("test.pdf", test_pdf_content, "application/pdf")
                        },
                        headers=api_key_headers,
                    )
                )

            responses = [f.result() for f in futures]
            assert all(r.status_code == 200 for r in responses)
            pdf_ids = [r.json()["pdf_id"] for r in responses]
            assert len(set(pdf_ids)) == 5  # Each upload should have unique ID


class TestContentExtraction:
    """Test Suite for Requirement 2: Text extraction and metadata storage"""

    def test_text_extraction_quality(self, test_pdf_content, api_key_headers):
        """Test accuracy of text extraction"""
        response = client.post(
            "/v1/pdf",
            files={"file": ("test.pdf", test_pdf_content, "application/pdf")},
            headers=api_key_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert "text_content" in content
        assert len(content["text_content"]) > 0
        assert "Test PDF Content" in content["text_content"]

    def test_metadata_storage(self, test_pdf_content, api_key_headers):
        """Test metadata extraction and storage"""
        response = client.post(
            "/v1/pdf",
            files={"file": ("test.pdf", test_pdf_content, "application/pdf")},
            headers=api_key_headers,
        )

        content = response.json()
        required_metadata = ["pdf_id", "filename", "size", "pages", "uploaded_at"]
        assert all(field in content for field in required_metadata)


class TestGeminiIntegration:
    """Test Suite for Requirement 3: Gemini API integration"""

    def test_chat_response_quality(self, test_pdf_content, api_key_headers):
        """Test quality of Gemini API responses"""
        # First upload PDF
        upload_response = client.post(
            "/v1/pdf",
            files={"file": ("test.pdf", test_pdf_content, "application/pdf")},
            headers=api_key_headers,
        )
        pdf_id = upload_response.json()["pdf_id"]

        # Test chat response
        chat_response = client.post(
            f"/v1/chat/{pdf_id}",
            json={"message": "What is this document about?"},
            headers=api_key_headers,
        )

        assert chat_response.status_code == 200
        response_content = chat_response.json()["response"]
        assert len(response_content) > 0
        assert "Test PDF Content" in response_content


class TestChatFunctionality:
    """Test Suite for Requirement 4: Chat functionality"""

    def test_chat_interaction_flow(self, test_pdf_content, api_key_headers):
        """Test complete chat interaction flow"""
        # Upload PDF
        upload_response = client.post(
            "/v1/pdf",
            files={"file": ("test.pdf", test_pdf_content, "application/pdf")},
            headers=api_key_headers,
        )
        pdf_id = upload_response.json()["pdf_id"]

        # Test multiple chat interactions
        questions = [
            "What is this document about?",
            "Can you summarize the main points?",
            "What are the key topics discussed?",
        ]

        for question in questions:
            response = client.post(
                f"/v1/chat/{pdf_id}",
                json={"message": question},
                headers=api_key_headers,
            )
            assert response.status_code == 200
            assert len(response.json()["response"]) > 0


class TestErrorHandling:
    """Test Suite for Requirement 5: Error handling and logging"""

    def test_invalid_file_handling(self, api_key_headers):
        """Test handling of invalid file uploads"""
        response = client.post(
            "/v1/pdf",
            files={"file": ("test.txt", b"Invalid content", "text/plain")},
            headers=api_key_headers,
        )
        assert response.status_code == 400
        assert "error" in response.json()

    def test_logging_functionality(self, caplog):
        """Test logging mechanisms"""
        with caplog.at_level("DEBUG"):
            client.get("/")
        assert len(caplog.records) > 0


class TestSecurity:
    """Test Suite for Requirement 6: Security measures"""

    def test_api_key_validation(self):
        """Test API key security"""
        response = client.post("/v1/pdf")  # No API key
        assert response.status_code == 403

    def test_rate_limiting(self, api_key_headers):
        """Test rate limiting functionality"""
        responses = []
        for _ in range(61):  # Exceed rate limit
            response = client.get("/", headers=api_key_headers)
            responses.append(response.status_code)
        assert 429 in responses


class TestPerformance:
    """Test Suite for Requirement 7: Performance optimization"""

    def test_large_file_handling(self, api_key_headers):
        """Test handling of large files"""
        large_content = b"0" * (5 * 1024 * 1024)  # 5MB file
        response = client.post(
            "/v1/pdf",
            files={"file": ("large.pdf", large_content, "application/pdf")},
            headers=api_key_headers,
        )
        assert response.status_code in [200, 413]  # Either success or file too large

    def test_concurrent_requests(self, api_key_headers):
        """Test handling of concurrent requests"""
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for _ in range(10):
                futures.append(
                    executor.submit(client.get, "/", headers=api_key_headers)
                )

            responses = [f.result() for f in futures]
            assert all(r.status_code in [200, 429] for r in responses)
