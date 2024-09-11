from langchain_community.embeddings import OllamaEmbeddings

from app.core.logger import get_logger
from app.models.base import ModelConfig
from app.models.embedding.base import BaseEmbedding

logger = get_logger()


class OllamaEmbedding(BaseEmbedding):
    def get_embedding_model(self, config: ModelConfig):
        try:
            logger.info(
                f"Initializing OllamaEmbeddings with model: {config.model_name}"
            )
            return OllamaEmbeddings(model=config.model_name, base_url=config.base_url)
        except Exception as err:
            logger.error(f"Failed to initialize OllamaEmbeddings: {str(err)}")
            raise RuntimeError("Failed to initialize OllamaEmbeddings.") from err
