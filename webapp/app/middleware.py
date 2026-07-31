"""Application middleware, including the in-process API rate limiter."""

from __future__ import annotations

from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from typing import Deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class InProcessRateLimiter:
    """A fixed-window limiter suitable for a single-process deployment.

    Requests are keyed by client IP address and retained only for ``window``
    seconds. State is local to this process; distributed deployments should use
    a shared store or an API gateway instead.
    """

    def __init__(self, limit: int = 60, window: float = 60.0) -> None:
        if limit < 1 or window <= 0:
            raise ValueError("limit must be positive and window must be greater than zero")
        self.limit = limit
        self.window = window
        self._requests: dict[str, Deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> tuple[bool, int]:
        """Record a request and return ``(allowed, remaining_requests)``."""
        now = monotonic()
        with self._lock:
            requests = self._requests[key]
            while requests and requests[0] <= now - self.window:
                requests.popleft()
            if len(requests) >= self.limit:
                return False, 0
            requests.append(now)
            return True, self.limit - len(requests)

    def reset(self) -> None:
        """Clear all counters, primarily for application lifecycle and tests."""
        with self._lock:
            self._requests.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests exceeding the configured in-process request limit."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Apply the limit before forwarding the request to an endpoint."""
        client_key = request.client.host if request.client else "unknown"
        limiter: InProcessRateLimiter = request.app.state.rate_limiter
        allowed, remaining = limiter.check(client_key)
        headers = {
            "X-RateLimit-Limit": str(limiter.limit),
            "X-RateLimit-Remaining": str(remaining),
        }
        if not allowed:
            headers["Retry-After"] = str(max(1, int(limiter.window)))
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please retry later.",
                },
                headers=headers,
            )

        response = await call_next(request)
        response.headers.update(headers)
        return response
