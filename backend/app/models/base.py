from abc import ABC, abstractmethod

from langchain.schema.language_model import BaseLanguageModel


class ModelFactory(ABC):
    @abstractmethod
    def get_chat_model(self) -> BaseLanguageModel:
        pass

    @abstractmethod
    def get_embedding_model(self):
        pass
