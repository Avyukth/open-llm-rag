from abc import ABC, abstractmethod
from langchain.embeddings.base import Embeddings
from langchain_community.embeddings import OllamaEmbeddings
from app.core.config import settings

class EmbeddingService(ABC):
    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        pass

class OllamaEmbeddingService(EmbeddingService):
    def get_embeddings(self) -> Embeddings:
        return OllamaEmbeddings(model=settings.MODEL, base_url=settings.OLLAMA_BASE_URL)
