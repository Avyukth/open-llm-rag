from abc import ABC, abstractmethod

from pydantic import BaseModel


class ModelConfig(BaseModel):
    provider: str
    model_name: str
    base_url: str = ""
    api_key: str = ""


class LLMFactory(ABC):
    @abstractmethod
    def get_chat_model(self, config: ModelConfig):
        pass


class EmbeddingFactory(ABC):
    @abstractmethod
    def get_embedding_model(self, config: ModelConfig):
        pass
