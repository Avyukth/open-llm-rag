from app.models.qa import AnswerWithSources
from langchain.prompts import PromptTemplate

from app.models import get_model_factory
from loguru import logger


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
    structured_model = model.with_structured_output(AnswerWithSources)
    logger.info("Initializing prompt", prompt)
    # Implement chain creation logic
    return structured_model, prompt
