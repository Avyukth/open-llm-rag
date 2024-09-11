import sys
import uuid
from contextvars import ContextVar

from app.core.config import settings
from fastapi import Request
from loguru import logger as loguru_logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

# Create a context variable to store request-specific data
request_id_context = ContextVar("request_id", default=None)


class RequestIdFilter:
    def __init__(self):
        self.request_id_context = request_id_context

    def __call__(self, record):
        record["extra"]["request_id"] = self.request_id_context.get()
        return record


# Remove the default logger
loguru_logger.remove()

# Add console logging
loguru_logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[request_id]}</cyan> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    filter=RequestIdFilter(),
    level=settings.LOG_LEVEL,
)

# Add file logging
loguru_logger.add(
    settings.LOG_FILE,
    rotation=settings.LOG_ROTATION,
    retention=settings.LOG_RETENTION,
    filter=RequestIdFilter(),
    level=settings.LOG_LEVEL,
)


class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        request_id_context.set(request_id)

        loguru_logger.info(f"Incoming request: {request.method} {request.url}")
        response = await call_next(request)
        loguru_logger.info(f"Request completed: {response.status_code}")

        # Add the request ID to the response headers
        response.headers["X-Request-ID"] = request_id

        return response


def get_logger():
    return loguru_logger
