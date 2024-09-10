from abc import ABC, abstractmethod

from app.models.base import ModelConfig


class BaseLLM(ABC):
    @abstractmethod
    def get_chat_model(self, config: ModelConfig):
        pass
