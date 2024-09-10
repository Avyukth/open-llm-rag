import requests
from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import ChatOllama

from app.core.config import settings
from app.core.logger import get_logger
from .base import ModelFactory

logger = get_logger()

class OllamaFactory(ModelFactory):
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model_name = settings.MODEL_NAME
        self._check_ollama_service()

    def _check_ollama_service(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            available_models = response.json()
            if self.model_name not in [model["name"] for model in available_models["models"]]:
                logger.error(f"Model '{self.model_name}' is not available. Available models: {[model['name'] for model in available_models['models']]}")
                raise ValueError(f"Model '{self.model_name}' is not available.")
            logger.info(f"Ollama service checked. Model '{self.model_name}' is available.")
        except requests.RequestException as err:
            logger.error(f"Failed to connect to Ollama service at {self.base_url}: {str(err)}")
            raise ConnectionError(f"Unable to connect to Ollama service at {self.base_url}.") from err

    def get_chat_model(self):
        try:
            logger.info(f"Initializing ChatOllama with model: {self.model_name}")
            return ChatOllama(model=self.model_name, temperature=0, base_url=self.base_url)
        except Exception as err:
            logger.error(f"Failed to initialize ChatOllama: {str(err)}")
            raise RuntimeError("Failed to initialize ChatOllama.") from err

    def get_embedding_model(self):
        try:
            logger.info(f"Initializing OllamaEmbeddings with model: {self.model_name}")
            return OllamaEmbeddings(model=self.model_name, base_url=self.base_url)
        except Exception as err:
            logger.error(f"Failed to initialize OllamaEmbeddings: {str(err)}")
            raise RuntimeError("Failed to initialize OllamaEmbeddings.") from err
