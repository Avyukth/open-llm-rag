from enum import Enum
from typing import Annotated, List, TypedDict

from pydantic import BaseModel


class Question(BaseModel):
    question: str


class AnswerWithSources(TypedDict):
    """An answer to the question, with sources."""

    answer: str
    sources: Annotated[
        List[str],
        ...,
        "List of sources (context chunk) used to answer the question",
    ]


class Answer(BaseModel):
    answer: str
    sources: List[str]


class Relevance(str, Enum):
    NON_RELEVANT = "NON_RELEVANT"
    PARTLY_RELEVANT = "PARTLY_RELEVANT"
    RELEVANT = "RELEVANT"


class EvaluationResult(BaseModel):
    relevance: Relevance
    explanation: str
