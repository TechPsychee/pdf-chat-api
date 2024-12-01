import os
import pytest
from pathlib import Path
from fpdf import FPDF
import shutil
from dotenv import load_dotenv

# Load test environment variables first
from . import test_env

# Now we can import app
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings

# Load environment variables from .env if they exist
load_dotenv()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def settings():
    return get_settings()


@pytest.fixture
def api_key_headers():
    return {"X-API-Key": os.getenv("API_KEY", "my-secure-api-key")}


@pytest.fixture
def test_pdf_content():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Test PDF Content", ln=1, align="C")
    pdf_buffer = pdf.output(dest="S").encode("latin-1")
    return pdf_buffer


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up test files after each test"""
    yield
    test_dirs = [Path(get_settings().UPLOAD_DIR), Path("data"), Path("test_uploads")]

    for dir_path in test_dirs:
        if dir_path.exists():
            shutil.rmtree(dir_path)
