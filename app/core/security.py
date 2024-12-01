from fastapi import Security, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS
from .config import get_settings
import time
from typing import Dict
from ..core.logging import setup_logging

settings = get_settings()
logger = setup_logging()

# API Key security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


def verify_api_key(api_key: str = Security(api_key_header)) -> bool:
    logger.debug(f"Expected API key: {settings.API_KEY}")
    logger.debug(f"Received API key: {api_key}")
    if not api_key or api_key != settings.API_KEY:
        logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Invalid or missing API key"
        )
    return True


# Rate limiting
class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.window_size = 60  # 1 minute window
        self.max_requests = settings.RATE_LIMIT_PER_MINUTE

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        if client_id not in self.requests:
            self.requests[client_id] = []

        # Remove old requests
        self.requests[client_id] = [
            req_time
            for req_time in self.requests[client_id]
            if now - req_time < self.window_size
        ]

        # Check if rate limit is exceeded
        if len(self.requests[client_id]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return False

        # Add new request
        self.requests[client_id].append(now)
        return True


rate_limiter = RateLimiter()


# Rate limit dependency
async def check_rate_limit(request: Request):
    client_id = request.client.host
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )
    return True
