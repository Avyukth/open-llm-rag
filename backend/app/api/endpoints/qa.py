from fastapi import APIRouter, Depends
from app.models.qa import Question, Answer
from app.core.dependencies import get_qa_service

qa_router = APIRouter()

@qa_router.post("/answer", response_model=Answer)
async def answer_question(question: Question, qa_service = Depends(get_qa_service)):
    return await qa_service.answer_question(question)
