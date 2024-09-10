from langchain_cohere import ChatCohere, CohereEmbeddings

from app.core.config import settings

from .base import ModelFactory


class CohereFactory(ModelFactory):
    def get_chat_model(self):
        return ChatCohere(
            model=settings.MODEL_NAME, cohere_api_key=settings.COHERE_API_KEY
        )

    def get_embedding_model(self):
        return CohereEmbeddings(
            model=settings.MODEL_NAME, cohere_api_key=settings.COHERE_API_KEY
        )
