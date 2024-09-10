from typing import List
from langchain.docstore.document import Document
from langchain.vectorstores import VectorStore
from app.services.document_processor import DocumentProcessor
from app.services.vector_store_service import VectorStoreService

class DocumentService:
    def __init__(self, document_processor: DocumentProcessor, vector_store_service: VectorStoreService):
        self.document_processor = document_processor
        self.vector_store_service = vector_store_service

    def process_document(self, file_path: str) -> VectorStore:
        documents = self.document_processor.process(file_path)
        return self.vector_store_service.create_vector_store(documents)
