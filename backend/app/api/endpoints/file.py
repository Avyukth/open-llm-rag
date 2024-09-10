from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.dependencies import get_file_service, set_qa_service
from app.services.file_service import FileService

file_router = APIRouter()


@file_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    original_filename: str = Form(...),
    file_service: FileService = Depends(get_file_service),
):
    result = await file_service.process_upload(file, original_filename)

    # Set the QAService instance
    print("result===========================", result)
    if "qa_service" in result:
        set_qa_service(result["qa_service"])
        del result["qa_service"]  # Remove from the response

    return result
