from app.core.config import settings
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate

def get_llm_chain():
    model = ChatOllama(model=settings.MODEL, temperature=0, base_url=settings.OLLAMA_BASE_URL)
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
    
    # Implement chain creation logic
    return model, prompt
