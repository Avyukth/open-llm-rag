from abc import ABC, abstractmethod
from typing import List

from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import VectorStore
from langchain_community.vectorstores import FAISS

from app.core.logger import get_logger

logger = get_logger()


class VectorStoreService(ABC):
    @abstractmethod
    def create_vector_store(
        self, documents: List[Document], embedding_model: Embeddings
    ) -> VectorStore:
        pass


class FAISSVectorStoreService(VectorStoreService):
    def create_vector_store(
        self, documents: List[Document], embedding_model: Embeddings
    ) -> VectorStore:
        logger.info(
            f"Creating FAISS vector store with embedding model: {type(embedding_model).__name__}"
        )
        return FAISS.from_documents(documents, embedding_model)
