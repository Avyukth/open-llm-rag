from typing import Callable

from fastapi import Depends, HTTPException

from app.services.document_processor import PDFProcessor
from app.services.document_service import DocumentService
from app.services.embedding_service import OllamaEmbeddingService
from app.services.qa_service import QAService
from app.services.vector_store_service import FAISSVectorStoreService

qa_service_instance = None


def get_qa_service():
    global qa_service_instance
    if qa_service_instance is None:
        raise HTTPException(
            status_code=400,
            detail="No document has been processed yet. Please upload a file first.",
        )
    return qa_service_instance


def set_qa_service(new_qa_service: QAService):
    global qa_service_instance
    qa_service_instance = new_qa_service


def get_document_processor():
    return PDFProcessor()


def get_embedding_service():
    return OllamaEmbeddingService()


def get_vector_store_service(
    embedding_service: OllamaEmbeddingService = Depends(get_embedding_service),
):
    return FAISSVectorStoreService(embedding_service)


def get_document_service(
    document_processor: PDFProcessor = Depends(get_document_processor),
    vector_store_service: FAISSVectorStoreService = Depends(get_vector_store_service),
):
    return DocumentService(document_processor, vector_store_service)


# Use a Callable type hint instead of importing FileService
def get_file_service(
    document_service: DocumentService = Depends(get_document_service),
) -> Callable:
    from app.services.file_service import (  # Import here to avoid circular import
        FileService,
    )

    return FileService(document_service)
