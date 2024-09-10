import os
import uuid

from fastapi import HTTPException, UploadFile
from loguru import logger

from app.core.config import settings
from app.services.document_service import DocumentService
from app.services.qa_service import QAService


class FileService:
    def __init__(self, document_service: DocumentService):
        self.document_service = document_service
        logger.info("FileService initialized with DocumentService")

    async def process_upload(self, file: UploadFile, original_filename: str):
        try:
            logger.info(f"Processing upload for file: {original_filename}")
            file_name, file_extension = os.path.splitext(original_filename)
            if not file_extension:
                file_extension = self._guess_extension(file.content_type)
                logger.info(f"Guessed file extension: {file_extension}")

            unique_filename = f"{uuid.uuid4().hex[:8]}{file_extension}"
            file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
            logger.info(f"Saving file to: {file_path}")

            with open(file_path, "wb") as buffer:
                contents = await file.read()
                buffer.write(contents)
            logger.success(f"File saved successfully: {file_path}")

            logger.info("Processing document with DocumentService")
            vector_store = self.document_service.process_document(file_path)
            logger.success("Document processed and vector store created")

            logger.info("Initializing QAService with the new vector store")
            qa_service = QAService(vector_store)

            logger.success("File upload and processing completed successfully")
            return {
                "original_filename": original_filename,
                "saved_filename": unique_filename,
                "detected_extension": file_extension,
                "status": "File uploaded and processed successfully",
                "qa_service": qa_service,
            }
        except Exception as e:
            logger.exception(f"Error processing upload: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _guess_extension(self, content_type):
        logger.info(f"Guessing file extension for content type: {content_type}")
        # Implementation of guessing file extension based on content type
        # Add your logic here
        guessed_extension = ".bin"  # Default extension
        logger.info(f"Guessed extension: {guessed_extension}")
        return guessed_extension
