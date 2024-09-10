# backend/main.py
from fastapi import FastAPI

from app.api.routes import router as api_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.BACKEND_PORT, reload=True)
