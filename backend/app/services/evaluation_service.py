import json
from operator import itemgetter
from typing import Dict, List

from app.core.logger import get_logger
from app.factories.llm_factory import get_llm
from app.models.evaluation import EvaluationRecord
from app.models.qa import Answer, EvaluationResult
from langchain.prompts import PromptTemplate
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

logger = get_logger()


class EvaluationService:
    def __init__(self):
        self.llm = get_llm()
        self.prompt = self._create_evaluation_prompt()
        self.chain = self._create_evaluation_chain()

    def _create_evaluation_prompt(self):
        template = """
        You are an expert evaluator for a RAG system.
        Your task is to analyze the relevance of the generated answer to the given question.
        Based on the relevance of the generated answer, you will classify it
        as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

        Here is the data for evaluation:

        Question: {question}
        Generated Answer: {answer}
        Question Relevance Sources: {sources}

        Please analyze the content and context of the generated answer in relation to the question and sources
        and provide your evaluation as follows:

        Relevance: [NON_RELEVANT | PARTLY_RELEVANT | RELEVANT]
        Explanation: [Provide a brief explanation for your evaluation]
        """
        return PromptTemplate(
            template=template, input_variables=["question", "answer", "sources"]
        )

    def _create_evaluation_chain(self):
        return (
            {
                "question": itemgetter("question"),
                "answer": itemgetter("answer"),
                "sources": itemgetter("sources"),
            }
            | self.prompt
            | self.llm.with_structured_output(EvaluationResult)
        )

    async def evaluate_answer(
        self, question: str, answer: str, sources: List[str]
    ) -> EvaluationResult:
        logger.info(f"Evaluating answer for question: {question}")
        return self.chain.invoke(
            {"question": question, "answer": answer, "sources": sources}
        )

    def calculate_mrr(self, relevance_list: List[bool]) -> float:
        for i, relevant in enumerate(relevance_list):
            if relevant:
                return 1.0 / (i + 1)
        return 0.0

    @staticmethod
    def _format_sources(sources: List[Dict]) -> str:
        formatted_sources = {str(i + 1): source for i, source in enumerate(sources)}
        return json.dumps(formatted_sources)

    async def evaluate_and_store(self, question: str, answer: Answer, db: Session):
        try:
            evaluation = await self.evaluate_answer(
                question, answer.answer, answer.sources
            )
            logger.info(f"Evaluating answer, evaluation: {evaluation}")

            record = EvaluationRecord(
                id=EvaluationRecord.create_id(question),
                question=question,
                answer=answer.answer,
                sources=self._format_sources(answer.sources),
                relevance=evaluation.relevance,
                explanation=evaluation.explanation,
            )

            # Perform an upsert operation
            stmt = insert(EvaluationRecord).values(
                id=record.id,
                question=record.question,
                answer=record.answer,
                sources=record.sources,
                relevance=record.relevance,
                explanation=record.explanation,
            )

            stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "answer": stmt.excluded.answer,
                    "sources": stmt.excluded.sources,
                    "relevance": stmt.excluded.relevance,
                    "explanation": stmt.excluded.explanation,
                },
            )

            db.execute(stmt)
            db.commit()

            logger.info(f"Evaluation upserted for question: {question}")
        except Exception as e:
            logger.exception(f"Error in background evaluation task: {str(e)}")
            db.rollback()
