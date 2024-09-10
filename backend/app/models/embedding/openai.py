from langchain_openai.embeddings import OpenAIEmbeddings

from ...models.base import ModelConfig
from .base import BaseEmbedding


class OpenAIEmbedding(BaseEmbedding):
    def get_embedding_model(self, config: ModelConfig):
        return OpenAIEmbeddings(model=config.model_name, api_key=config.api_key)
