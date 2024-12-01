from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware  # Fixed the typo here
from ..core.security import rate_limiter, request_tracker
import time
import gzip
import asyncio
from typing import Optional


class PerformanceMiddleware(BaseHTTPMiddleware):  # Fixed here too
    async def dispatch(self, request: Request, call_next):
        # Check rate limit
        client_id = request.client.host
        if not rate_limiter.is_allowed(client_id):
            return Response(content="Rate limit exceeded", status_code=429)

        # Track concurrent requests
        if not request_tracker.start_request():
            return Response(content="Server is busy", status_code=503)

        try:
            # Start timing
            start_time = time.time()

            # Process request
            response = await call_next(request)

            # Compress response if needed
            if response.headers.get("content-type") == "application/json":
                content = await response.body()
                if len(content) > 1024:  # Only compress responses > 1KB
                    compressed = gzip.compress(content)
                    return Response(
                        content=compressed,
                        headers={**response.headers, "Content-Encoding": "gzip"},
                        status_code=response.status_code,
                    )

            return response

        finally:
            # End request tracking
            request_tracker.end_request()

            # Log performance metrics
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
