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


# class QAService:
#     def __init__(self, vector_store: VectorStore):
#         self.vector_store = vector_store
#         self.llm = get_llm()
#         self.retriever = self.vector_store.as_retriever()
#         self.prompt = self._create_prompt()
#         self.chain = self._create_chain()
#         self.evaluation_service = EvaluationService()
#         logger.info("QAService initialized with vector store and LLM")

#     def _create_prompt(self):
#         template = """
#         You are an assistant that provides answers to questions based on
#         a given context.

#         Answer the question based on the context. If you can't answer the
#         question, reply "I don't know".

#         Be as concise as possible and go straight to the point.

#         Context: {context}

#         Question: {question}
#         """
#         return PromptTemplate(template=template, input_variables=["context", "question"])

#     def _create_chain(self):
#         return LLMChain(llm=self.llm, prompt=self.prompt)

#     async def answer_question(self, question: Question) -> Answer:
#         try:
#             logger.info(f"Received question: {question.question}")
#             context = self.retriever.get_relevant_documents(question.question)
#             result = self.chain.run(context=context, question=question.question)
#             logger.info(f"Generated answer: {result}")

#             # Evaluate the answer
#             evaluation = await self.evaluation_service.evaluate_answer(question.question, result)
#             logger.info(f"Answer evaluation: {evaluation}")

#             return Answer(answer=result, sources=context, evaluation=evaluation)
#         except Exception as e:
#             logger.exception(f"Error processing question: {str(e)}")
#             raise HTTPException(status_code=500, detail=str(e))

################################################################################
# async def evaluate_qa_system(self, questions: List[Question]) -> dict:
#     evaluations = []
#     for question in questions:
#         answer = await self.answer_question(question)
#         evaluations.append(answer.evaluation)

#     relevance_scores = [1 if eval.relevance == "RELEVANT" else 0 for eval in evaluations]
#     mrr = self.evaluation_service.calculate_mrr(relevance_scores)

#     return {
#         "evaluations": evaluations,
#         "mean_reciprocal_rank": mrr
#     }
