import secrets

from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv


class Settings(BaseSettings):
    # General Settings
    APP_NAME: str = "PDF Chat API"
    DEBUG: bool = True
    API_V1_STR: str = "/v1"
    PROJECT_ROOT: str = "."

    # Gemini API
    GEMINI_API_KEY: str

    # PDF Settings
    API_KEY: str = secrets.token_urlsafe(32)  # Default only if not set in .env
    MAX_PDF_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    # LLM Settings
    MAX_INPUT_LENGTH: int = 4096
    MAX_OUTPUT_LENGTH: int = 8196

    # Storage Settings
    STORAGE_TYPE: str = "local"
    USE_ASYNC_IO: bool = True
    COMPRESSION_ENABLED: bool = True

    # Security Settings
    ALLOWED_HOSTS: list = ["*"]
    API_KEY_HEADER: str = "X-API-Key"
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_CONCURRENT_REQUESTS: int = 100

    MAX_CHUNKS_PER_REQUEST: int = 10
    EMBEDDING_CHUNK_SIZE: int = 500

    # Performance Settings
    CHUNK_SIZE: int = 1000
    MAX_CHUNKS_PER_REQUEST: int = 10
    CACHE_TTL: int = 3600

    # Configuration for .env support
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()


def create_upload_dir():
    """Create upload directory if it doesn't exist"""
    upload_path = Path(get_settings().UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)


def create_necessary_directories():
    """Create all necessary directories"""
    dirs = [get_settings().UPLOAD_DIR, "logs", "data"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
