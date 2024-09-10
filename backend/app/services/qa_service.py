import json
from operator import itemgetter
from typing import List, Union

from langchain.vectorstores import VectorStore
from loguru import logger

from app.models.qa import Answer, AnswerWithSources, Question
from app.services.llm_factory import get_llm_chain

class QAService:
    def __init__(self, vector_store: VectorStore):
        self.model, self.prompt = get_llm_chain()
        logger.info("Initializing llm Chain=============================", self.model, self.prompt)
        self.retriever = vector_store.as_retriever()
        logger.info("Initializing as_retriever", self.retriever)
        self.chain = self._create_chain()

    def _create_chain(self):
        return (
            {
                "context": itemgetter("question") | self.retriever,
                "question": itemgetter("question"),
            }
            | self.prompt
            | self.model
        )

    async def answer_question(self, question: Question) -> Answer:
        try:
            logger.info(f"Received question: {question.question}")
            logger.info(f"Received prompt: {self.prompt}")
            result = self.chain.invoke({"question": question.question})
            logger.info(f"Generated answer: {result}")

            answer, sources = self._parse_result(result)
            return Answer(answer=answer, sources=sources)
        except Exception as e:
            logger.exception(f"Error processing question: {str(e)}")
            raise

    def _parse_result(self, result: Union[str, dict]) -> tuple[str, List[str]]:
        if isinstance(result, str):
            # Handle string result (unlikely, but just in case)
            return result, []
        elif isinstance(result, dict):
            # Handle dictionary result
            if "answer" in result and "sources" in result:
                # New format
                answer = result["answer"]
                sources = self._parse_sources(result["sources"])
            elif "answer" in result:
                # Previous format
                answer = result["answer"]
                sources = self._parse_sources(result.get("sources", []))
            else:
                # Unexpected format
                raise ValueError(f"Unexpected result structure: {result}")
            return answer, sources
        else:
            raise ValueError(f"Unexpected result type: {type(result)}")

    def _parse_sources(self, sources: Union[str, List[str], List[dict]]) -> List[str]:
        if isinstance(sources, list):
            if all(isinstance(s, str) for s in sources):
                return sources
            elif all(isinstance(s, dict) for s in sources):
                # Handle Document objects
                return [
                    f"Document from {s.get('metadata', {}).get('source', 'unknown source')}"
                    for s in sources
                ]
        elif isinstance(sources, str):
            try:
                parsed_sources = json.loads(sources)
                if isinstance(parsed_sources, list):
                    return parsed_sources
            except json.JSONDecodeError:
                pass
            # If JSON parsing fails or doesn't result in a list, split the string
            return [s.strip() for s in sources.strip("[]").split(",")]
        return []
