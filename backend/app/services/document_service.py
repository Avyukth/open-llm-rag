from langchain.vectorstores import VectorStore

from app.core.logger import get_logger
from app.services.document_processor import DocumentProcessor
from app.services.vector_store_service import VectorStoreService

logger = get_logger()


class DocumentService:
    def __init__(
        self,
        document_processor: DocumentProcessor,
        vector_store_service: VectorStoreService,
    ):
        self.document_processor = document_processor
        self.vector_store_service = vector_store_service
        logger.info("DocumentService initialized")

    def process_document(self, file_path: str) -> VectorStore:
        logger.info(f"Processing document: {file_path}")
        documents = self.document_processor.process(file_path)
        logger.info("Document processed, creating vector store")
        vector_store = self.vector_store_service.create_vector_store(documents)
        logger.info("Vector store created successfully")
        return vector_store
