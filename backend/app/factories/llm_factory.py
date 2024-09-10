from app.core.config import settings
from app.core.logger import get_logger
from app.models import model_service
from app.models.base import ModelConfig

logger = get_logger()


class LLMFactory:
    @staticmethod
    def create_llm():
        logger.info(f"Creating LLM with provider: {settings.LLM.provider_type}")
        config = ModelConfig(
            provider=settings.LLM.provider_type,
            model_name=settings.LLM.name,
            base_url=settings.LLM.base_url,
            api_key=settings.LLM.api_key,
        )
        try:
            llm = model_service.get_llm(config)
            logger.info(f"LLM created successfully: {type(llm).__name__}")
            return llm
        except Exception as e:
            logger.error(f"Error creating LLM: {str(e)}")
            raise


def get_llm():
    return LLMFactory.create_llm()
