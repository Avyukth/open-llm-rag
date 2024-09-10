from app.core.config import settings

from .base import ModelFactory
from .cohere import CohereFactory
from .ollama import OllamaFactory
from .openai import OpenAIFactory


def get_model_factory() -> ModelFactory:
    factories = {
        "ollama": OllamaFactory,
        "openai": OpenAIFactory,
        "cohere": CohereFactory,
    }
    factory_class = factories.get(settings.MODEL_PROVIDER)
    if not factory_class:
        raise ValueError(f"Unsupported model provider: {settings.MODEL_PROVIDER}")
    return factory_class()
