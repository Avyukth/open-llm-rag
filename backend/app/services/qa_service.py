import json
from operator import itemgetter
from typing import List, Union

from langchain.vectorstores import VectorStore

from app.core.logger import get_logger
from app.models.qa import Answer, AnswerWithSources, Question
from app.services.llm_factory import get_llm_chain

logger = get_logger()

class QAService:
    def __init__(self, vector_store: VectorStore):
        self.model, self.prompt = get_llm_chain()
        logger.info("Initializing QAService with LLM chain and vector store")
        self.retriever = vector_store.as_retriever()
        self.chain = self._create_chain()

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
        try:
            logger.info("Processing question")
            result = self.chain.invoke({"question": question.question})
            logger.info("Answer generated successfully")

            answer, sources = self._parse_result(result)
            return Answer(answer=answer, sources=sources)
        except Exception as e:
            logger.exception(f"Error processing question: {str(e)}")
            raise

    def _parse_result(self, result: Union[str, dict]) -> tuple[str, List[str]]:
        try:
            if isinstance(result, str):
                return result, []
            elif isinstance(result, dict):
                if "answer" in result and "sources" in result:
                    answer = result["answer"]
                    sources = self._parse_sources(result["sources"])
                elif "answer" in result:
                    answer = result["answer"]
                    sources = self._parse_sources(result.get("sources", []))
                else:
                    raise ValueError(f"Unexpected result structure: {result}")
                return answer, sources
            else:
                raise ValueError(f"Unexpected result type: {type(result)}")
        except Exception as e:
            logger.error(f"Error parsing result: {str(e)}")
            raise

    def _parse_sources(self, sources: Union[str, List[str], List[dict]]) -> List[str]:
        try:
            if isinstance(sources, list):
                if all(isinstance(s, str) for s in sources):
                    return sources
                elif all(isinstance(s, dict) for s in sources):
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
                return [s.strip() for s in sources.strip("[]").split(",")]
            return []
        except Exception as e:
            logger.error(f"Error parsing sources: {str(e)}")
            return []
