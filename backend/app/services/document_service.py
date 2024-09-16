import os

from app.core.logger import get_logger
from app.factories.embedding_factory import get_embedding_model
from app.services.document_processor import DocumentProcessor, PDFProcessor
from app.services.vector_store_service import VectorStoreService
from langchain.vectorstores import VectorStore

logger = get_logger()


class DocumentService:
    def __init__(self, vector_store_service: VectorStoreService):
        self.vector_store_service = vector_store_service
        logger.info("DocumentService initialized")

    def process_document(self, file_path: str) -> VectorStore:
        logger.info(f"Processing document: {file_path}")
        processor = self._get_document_processor(file_path)
        documents = processor.process(file_path)
        logger.info("Document processed, creating vector store")
        embedding_model = get_embedding_model()
        vector_store = self.vector_store_service.create_vector_store(
            documents, embedding_model
        )
        logger.info("Vector store created successfully")
        return vector_store

    def _get_document_processor(self, file_path: str) -> DocumentProcessor:
        _, file_extension = os.path.splitext(file_path)
        processors = {
            ".pdf": PDFProcessor,
        }
        processor_class = processors.get(file_extension.lower())
        if not processor_class:
            raise ValueError(f"Unsupported file type: {file_extension}")
        return processor_class()
