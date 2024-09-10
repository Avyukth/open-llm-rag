import os
import uuid
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from app.services.document_service import DocumentService
from app.services.qa_service import QAService
from app.core.dependencies import set_qa_service

class FileService:
    def __init__(self, document_service: DocumentService):
        self.document_service = document_service

    async def process_upload(self, file: UploadFile, original_filename: str):
        try:
            file_name, file_extension = os.path.splitext(original_filename)
            if not file_extension:
                file_extension = self._guess_extension(file.content_type)

            unique_filename = f"{uuid.uuid4().hex[:8]}{file_extension}"
            file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

            with open(file_path, "wb") as buffer:
                contents = await file.read()
                buffer.write(contents)

            # Process the document using DocumentService
            vector_store = self.document_service.process_document(file_path)

            # Initialize QAService with the new vector store
            qa_service = QAService(vector_store)

            # Set the new QAService as the current instance
            set_qa_service(qa_service)

            return {
                "original_filename": original_filename,
                "saved_filename": unique_filename,
                "detected_extension": file_extension,
                "status": "File uploaded and processed successfully",
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _guess_extension(self, content_type):
        # Implementation of guessing file extension based on content type
        pass
