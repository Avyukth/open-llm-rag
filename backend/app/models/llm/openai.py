from langchain_openai import ChatOpenAI

from app.models.base import ModelConfig
from app.models.llm.base import BaseLLM


class OpenAILLM(BaseLLM):
    def get_chat_model(self, config: ModelConfig):
        return ChatOpenAI(model=config.model_name, api_key=config.api_key)
