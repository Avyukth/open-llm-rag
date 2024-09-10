import requests
from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import ChatOllama

from app.core.config import settings

from .base import ModelFactory
from app.core.logger import get_logger
logger = get_logger()

class OllamaFactory(ModelFactory):
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model_name = settings.MODEL_NAME
        self._check_ollama_service()

    def _check_ollama_service(self):
        try:
            logger.info(f"base url =================={self.base_url}")

            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            available_models = response.json()
            if self.model_name not in [
                model["name"] for model in available_models["models"]
            ]:
                raise ValueError(
                    f"Model '{self.model_name}' is not available. Available models: {[model['name'] for model in available_models['models']]}"
                )
        except requests.RequestException as e:
            logger.error(
                f"Failed to connect to Ollama service at {self.base_url}: {str(e)}"
            )
            raise ConnectionError(
                f"Unable to connect to Ollama service at {self.base_url}. Please ensure the service is running and accessible."
            )

    def get_chat_model(self):
        try:
            logger.info(f"Initializing ChatOllama with model: {self.model_name}")
            return ChatOllama(
                model=self.model_name, temperature=0, base_url=self.base_url
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChatOllama: {str(e)}")
            raise

    def get_embedding_model(self):
        try:
            logger.info(f"Initializing OllamaEmbeddings with model: {self.model_name}")
            return OllamaEmbeddings(model=self.model_name, base_url=self.base_url)
        except Exception as e:
            logger.error(f"Failed to initialize OllamaEmbeddings: {str(e)}")
            raise


# Usage:
# factory = OllamaFactory()
# chat_model = factory.get_chat_model()
# embedding_model = factory.get_embedding_model()
