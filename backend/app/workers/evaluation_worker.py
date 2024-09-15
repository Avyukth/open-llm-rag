# app/workers/evaluation_worker.py
import json

from app.core.config import settings
from app.models.evaluation import EvaluationRecord
from app.services.evaluation_service import get_evaluation_service
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

celery_app = Celery("evaluation_worker", broker=settings.CELERY_BROKER_URL)

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task
def evaluate_and_store(question: str, answer: str, sources: list):
    evaluation_service = get_evaluation_service()
    evaluation_result = evaluation_service.evaluate_answer(question, answer)

    db = SessionLocal()
    try:
        evaluation_record = EvaluationRecord(
            question=question,
            answer=answer,
            sources=json.dumps(sources),
            relevance=evaluation_result.relevance,
            explanation=evaluation_result.explanation,
        )
        db.add(evaluation_record)
        db.commit()
    finally:
        db.close()

    return evaluation_result.dict()
