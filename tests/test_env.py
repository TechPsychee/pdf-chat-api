# tests/test_env.py
import os

# Test environment settings
TEST_SETTINGS = {
    "GEMINI_API_KEY": "test-gemini-api-key",
    "API_KEY": "my-secure-api-key",
    "DEBUG": "True",
    "UPLOAD_DIR": "test_uploads",
    "MAX_FILE_SIZE": "10485760",  # 10MB in bytes
}

# Set environment variables
for key, value in TEST_SETTINGS.items():
    os.environ[key] = value
