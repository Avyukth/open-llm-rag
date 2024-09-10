from langchain.prompts import PromptTemplate

from app.core.logger import get_logger
from app.models import get_model_factory

logger = get_logger()


def get_llm_chain():
    model_factory = get_model_factory()
    model = model_factory.get_chat_model()

    template = """
        You are an assistant that provides answers to questions based on
        a given context.

        Answer the question based on the context. If you can't answer the
        question, reply "I don't know".

        Be as concise as possible and go straight to the point.

        Context: {context}

        Question: {question}
        """
    prompt = PromptTemplate.from_template(template)
    logger.info("LLM chain initialized with prompt template")
    return model, prompt
