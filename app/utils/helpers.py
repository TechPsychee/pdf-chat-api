import hashlib
from pathlib import Path
from typing import List, Dict
from fastapi import HTTPException
from ..core.config import get_settings

settings = get_settings()


def generate_file_hash(content: bytes) -> str:
    """
    Generate a hash for file content
    """
    return hashlib.sha256(content).hexdigest()


def get_file_path(pdf_id: str) -> Path:
    """
    Get the full path for a PDF file
    """
    return Path(settings.UPLOAD_DIR) / f"{pdf_id}.pdf"


def validate_file_type(filename: str) -> bool:
    """
    Validate if the file is a PDF
    """
    return filename.lower().endswith(".pdf")


def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """
    Split text into chunks for processing
    """
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
