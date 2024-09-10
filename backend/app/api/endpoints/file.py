from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.dependencies import get_file_service, set_qa_service
from app.core.logger import get_logger
from app.services.file_service import FileService

logger = get_logger()
file_router = APIRouter()


@file_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    original_filename: str = Form(...),
    model_provider: str = Form(default="ollama"),  # Note the lowercase default
    model_name: str = Form(default="llama3.1:8b"),
    file_service: FileService = Depends(get_file_service),
):
    logger.info(f"Received file upload request: {original_filename}")
    logger.info(f"Selected model provider: {model_provider}, model: {model_name}")

    result = await file_service.process_upload(
        file, original_filename, model_provider, model_name
    )

    if "qa_service" in result:
        set_qa_service(result["qa_service"])
        logger.info("QA service instance has been set")
        del result["qa_service"]  # Remove from the response

    logger.info(f"File upload processed successfully: {original_filename}")
    return result
