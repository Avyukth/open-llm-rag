# backend/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logger import LoggerMiddleware, get_logger

logger = get_logger()

app = FastAPI(title=settings.PROJECT_NAME)

# Add LoggerMiddleware
app.add_middleware(LoggerMiddleware)

app.include_router(api_router, prefix="/api")


# Add exception handler for logging unhandled exceptions
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on http://0.0.0.0:{settings.BACKEND_PORT}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=True,
        log_level="info",
    )
