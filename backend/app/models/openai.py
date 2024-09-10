from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

from app.core.config import settings

from .base import ModelFactory


class OpenAIFactory(ModelFactory):
    def get_chat_model(self):
        return ChatOpenAI(model=settings.MODEL_NAME, api_key=settings.OPENAI_API_KEY)

    def get_embedding_model(self):
        return OpenAIEmbeddings(
            model=settings.MODEL_NAME, api_key=settings.OPENAI_API_KEY
        )
