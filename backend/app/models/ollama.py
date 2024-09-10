from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings

from app.core.config import settings

from .base import ModelFactory


class OllamaFactory(ModelFactory):
    def get_chat_model(self):
        return ChatOllama(
            model=settings.MODEL_NAME, temperature=0, base_url=settings.OLLAMA_BASE_URL
        )

    def get_embedding_model(self):
        return OllamaEmbeddings(
            model=settings.MODEL_NAME, base_url=settings.OLLAMA_BASE_URL
        )
