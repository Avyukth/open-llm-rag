from fastapi import APIRouter, Depends

from app.core.dependencies import get_qa_service
from app.models.qa import Answer, Question
from app.core.logger import get_logger

logger = get_logger()
qa_router = APIRouter()

@qa_router.post("/answer", response_model=Answer)
async def answer_question(question: Question, qa_service=Depends(get_qa_service)):
    logger.info(f"Received question: {question.question}")  # Changed from question.query to question.question
    answer = await qa_service.answer_question(question)
    logger.info("Question answered successfully")
    return answer
