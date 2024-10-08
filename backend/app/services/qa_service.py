import json
from operator import itemgetter

from app.core.logger import get_logger
from app.factories.llm_factory import get_llm
from app.models.qa import Answer, AnswerWithSources, Question
from fastapi import HTTPException
from langchain.prompts import PromptTemplate
from langchain.vectorstores import VectorStore

logger = get_logger()


class QAService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.llm = get_llm()
        self.retriever = self.vector_store.as_retriever()
        self.prompt = self._create_prompt()
        self.chain = self._create_chain()
        logger.info("QAService initialized with vector store and LLM")

    def _create_chain(self):
        return (
            {
                "context": itemgetter("question") | self.retriever,
                "question": itemgetter("question"),
            }
            | self.prompt
            | self.llm.with_structured_output(AnswerWithSources)
        )

    def _create_prompt(self):
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
        return prompt

    async def answer_question(self, question: Question) -> Answer:
        try:
            logger.info(f"Received question: {question.question}")
            result = self.chain.invoke({"question": question.question})
            logger.info(f"Generated answer: {result}")

            if isinstance(result, dict) and "answer" in result and "sources" in result:
                try:
                    sources = json.loads(result["sources"])
                except json.JSONDecodeError:
                    sources = [
                        s.strip() for s in result["sources"].strip("[]").split(",")
                    ]

                return Answer(answer=result["answer"], sources=sources)
            else:
                logger.error(f"Unexpected result structure: {result}")
                raise HTTPException(
                    status_code=500,
                    detail="Unexpected response structure from the chain",
                )
        except Exception as e:
            logger.exception(f"Error processing question: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
