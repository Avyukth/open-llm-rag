from langchain.vectorstores import VectorStore

from app.core.logger import get_logger
from app.factories.llm_factory import get_llm
from app.models.qa import Answer, Question

logger = get_logger()


class QAService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.llm = get_llm()
        logger.info("QAService initialized with vector store and LLM")

    async def answer_question(self, question: Question) -> Answer:
        try:
            logger.info(f"Processing question: {question.question}")
            context = self.vector_store.similarity_search(question.question, k=3)
            context_text = "\n".join([doc.page_content for doc in context])

            prompt = f"""
            Context: {context_text}

            Question: {question.question}

            Answer the question based on the given context. If you can't answer the question, reply "I don't know".
            Be concise and to the point.
            """

            response = await self.llm.agenerate([prompt])
            answer = response.generations[0][0].text.strip()
            logger.info("Answer generated successfully")

            sources = [doc.metadata.get("source", "Unknown") for doc in context]
            return Answer(answer=answer, sources=sources)
        except Exception as e:
            logger.exception(f"Error processing question: {str(e)}")
            raise
