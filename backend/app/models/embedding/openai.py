from langchain_openai.embeddings import OpenAIEmbeddings

from app.models.base import ModelConfig
from app.models.embedding.base import BaseEmbedding


class OpenAIEmbedding(BaseEmbedding):
    def get_embedding_model(self, config: ModelConfig):
        return OpenAIEmbeddings(model=config.model_name, api_key=config.api_key)
