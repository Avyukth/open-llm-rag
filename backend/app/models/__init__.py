from app.core.logger import get_logger

from .base import ModelConfig
from .embedding.ollama import OllamaEmbedding
from .embedding.openai import OpenAIEmbedding
from .llm.ollama import OllamaLLM
from .llm.openai import OpenAILLM

logger = get_logger()


class ModelService:
    def __init__(self):
        self.llm_factories = {
            "ollama": OllamaLLM(),
            "openai": OpenAILLM(),
        }
        self.embedding_factories = {
            "ollama": OllamaEmbedding(),
            "openai": OpenAIEmbedding(),
        }

    def get_llm(self, config: ModelConfig):
        factory = self.llm_factories.get(config.provider.lower())
        if not factory:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")
        return factory.get_chat_model(config)

    def get_embedding_model(self, config: ModelConfig):
        factory = self.embedding_factories.get(config.provider.lower())
        if not factory:
            raise ValueError(f"Unsupported embedding provider: {config.provider}")
        return factory.get_embedding_model(config)


def get_model_service() -> ModelService:
    return ModelService()


model_service = get_model_service()
