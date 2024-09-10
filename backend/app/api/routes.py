from fastapi import APIRouter, Depends
from app.api.endpoints import file_router, qa_router
from app.core.dependencies import get_qa_service

router = APIRouter()

router.include_router(file_router, prefix="/files", tags=["files"])
router.include_router(
    qa_router,
    prefix="/qa",
    tags=["qa"],
    dependencies=[Depends(get_qa_service)]
)
