from abc import ABC, abstractmethod


class ModelFactory(ABC):
    @abstractmethod
    def get_chat_model(self):
        pass

    @abstractmethod
    def get_embedding_model(self):
        pass
