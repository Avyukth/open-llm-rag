import requests
from langchain_ollama import ChatOllama

from app.core.logger import get_logger

from ...models.base import ModelConfig
from .base import BaseLLM

logger = get_logger()


class OllamaLLM(BaseLLM):
    def get_chat_model(self, config: ModelConfig):
        self._check_ollama_service(config)
        try:
            logger.info(f"Initializing ChatOllama with model: {config.model_name}")
            return ChatOllama(
                model=config.model_name, temperature=0, base_url=config.base_url
            )
        except Exception as err:
            logger.error(f"Failed to initialize ChatOllama: {str(err)}")
            raise RuntimeError("Failed to initialize ChatOllama.") from err

    def _check_ollama_service(self, config: ModelConfig):
        try:
            response = requests.get(f"{config.base_url}/api/tags")
            response.raise_for_status()
            available_models = response.json()
            if config.model_name not in [
                model["name"] for model in available_models["models"]
            ]:
                logger.error(
                    f"Model '{config.model_name}' is not available. Available models: {[model['name'] for model in available_models['models']]}"
                )
                raise ValueError(f"Model '{config.model_name}' is not available.")
            logger.info(
                f"Ollama service checked. Model '{config.model_name}' is available."
            )
        except requests.RequestException as err:
            logger.error(
                f"Failed to connect to Ollama service at {config.base_url}: {str(err)}"
            )
            raise ConnectionError(
                f"Unable to connect to Ollama service at {config.base_url}."
            ) from err
