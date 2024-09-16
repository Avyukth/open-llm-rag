from app.core.dependencies import get_file_service, set_qa_service
from app.core.logger import get_logger
from app.services.file_service import FileService
from fastapi import APIRouter, Depends, File, Form, UploadFile

logger = get_logger()
file_router = APIRouter()


@file_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    original_filename: str = Form(...),
    file_service: FileService = Depends(get_file_service),
):
    logger.info(f"Received file upload request: {original_filename}")

    result = await file_service.process_upload(file, original_filename)

    if "qa_service" in result:
        set_qa_service(result["qa_service"])
        logger.info("QA service instance has been set")
        del result["qa_service"]

    logger.info(f"File upload processed successfully: {original_filename}")
    return result
