# app/services/vector_store_service.py
from abc import ABC, abstractmethod
from typing import List
from langchain.docstore.document import Document
from langchain.vectorstores import VectorStore
from langchain_community.vectorstores import FAISS
from app.services.embedding_service import EmbeddingService

class VectorStoreService(ABC):
    @abstractmethod
    def create_vector_store(self, documents: List[Document]) -> VectorStore:
        pass

class FAISSVectorStoreService(VectorStoreService):
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service

    def create_vector_store(self, documents: List[Document]) -> VectorStore:
        embeddings = self.embedding_service.get_embeddings()
        return FAISS.from_documents(documents, embeddings)
