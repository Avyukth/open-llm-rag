from app.core.config import settings
from app.core.logger import get_logger
from app.models import model_service
from app.models.base import ModelConfig

logger = get_logger()


class EmbeddingFactory:
    @staticmethod
    def create_embedding_model():
        logger.info(
            f"Creating Embedding model with provider: {settings.EMBEDDING.provider_type}"
        )
        config = ModelConfig(
            provider=settings.EMBEDDING.provider_type,
            model_name=settings.EMBEDDING.name,
            base_url=settings.EMBEDDING.base_url,
            api_key=settings.EMBEDDING.api_key,
        )
        try:
            embedding_model = model_service.get_embedding_model(config)
            logger.info(
                f"Embedding model created successfully: {type(embedding_model).__name__}"
            )
            return embedding_model
        except Exception as e:
            logger.error(f"Error creating Embedding model: {str(e)}")
            raise


def get_embedding_model():
    return EmbeddingFactory.create_embedding_model()
