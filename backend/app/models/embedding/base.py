from abc import ABC, abstractmethod

from app.models.base import ModelConfig


class BaseEmbedding(ABC):
    @abstractmethod
    def get_embedding_model(self, config: ModelConfig):
        pass
