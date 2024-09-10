from app.core.logger import get_logger
from app.factories.model_factory import ModelFactory

logger = get_logger()


class ModelService:
    def __init__(self):
        self.model_factory = ModelFactory()

    def get_chat_model(self, provider: str = None):
        logger.info(f"Getting chat model for provider: {provider}")
        return self.model_factory.get_chat_model(provider)

    def get_embedding_model(self, provider: str = None):
        logger.info(f"Getting embedding model for provider: {provider}")
        return self.model_factory.get_embedding_model(provider)
