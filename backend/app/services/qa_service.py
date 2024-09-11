import json
from langchain.vectorstores import VectorStore

from app.core.logger import get_logger
from app.factories.llm_factory import get_llm
from app.models.qa import Answer, Question, AnswerWithSources
from operator import itemgetter
logger = get_logger()


class QAService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.llm = get_llm()
        self.retriever = self.vector_store.as_retriever()
        self.chain = self._create_chain()
        logger.info("QAService initialized with vector store and LLM")

    def _create_chain(self):
        return (
            {
                "context": itemgetter("question") | self.retriever,
                "question": itemgetter("question"),
            }
            | self.prompt
            | self.model.with_structured_output(AnswerWithSources)
        )

    async def answer_question(self, question: Question) -> Answer:
        # try:
        #     logger.info(f"Processing question: {question.question}")
        #     context = self.vector_store.similarity_search(question.question, k=3)
        #     context_text = "\n".join([doc.page_content for doc in context])

        #     prompt = f"""
        #     Context: {context_text}

        #     Question: {question.question}

        #     Answer the question based on the given context. If you can't answer the question, reply "I don't know".
        #     Be concise and to the point.
        #     """

        #     response = await self.llm.agenerate([prompt])
        #     answer = response.generations[0][0].text.strip()
        #     logger.info("Answer generated successfully")

        #     sources = [doc.metadata.get("source", "Unknown") for doc in context]
        #     return Answer(answer=answer, sources=sources)
        # except Exception as e:
        #     logger.exception(f"Error processing question: {str(e)}")
        #     raise
        try:
            logger.info(f"Received question: {question.question}")
            result = chain.invoke({"question": question.question})
            logger.info(f"Generated answer: {result}")

            if isinstance(result, dict) and "answer" in result and "sources" in result:
                try:
                    sources = json.loads(result["sources"])
                except json.JSONDecodeError:
                    sources = [s.strip() for s in result["sources"].strip("[]").split(",")]

                return Answer(answer=result["answer"], sources=sources)
            else:
                logger.error(f"Unexpected result structure: {result}")
                raise HTTPException(
                    status_code=500, detail="Unexpected response structure from the chain"
                )
        except Exception as e:
            logger.exception(f"Error processing question: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
