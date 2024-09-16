import time
from typing import Dict

import weave
from app.core.database import engine, get_db
from app.core.dependencies import get_evaluation_service, get_qa_service
from app.core.logger import get_logger
from app.core.wandb_utils import finish_wandb, init_wandb, log_qa_metrics
from app.models.evaluation import Base, EvaluationRecord
from app.models.qa import Answer, Question
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

logger = get_logger()
qa_router = APIRouter()
wandb_enabled = False
Base.metadata.create_all(bind=engine)


@qa_router.on_event("startup")
async def startup_event():
    global wandb_enabled
    wandb_enabled = init_wandb()


@qa_router.on_event("shutdown")
async def shutdown_event():
    if wandb_enabled:
        finish_wandb()


@weave.op()
@qa_router.post("/answer", response_model=Answer)
async def answer_question(
    question: Question,
    background_tasks: BackgroundTasks,
    qa_service=Depends(get_qa_service),
    evaluation_service=Depends(get_evaluation_service),
    db: Session = Depends(get_db),
):
    try:
        logger.info("Received question request")
        start_time = time.time()
        answer = await qa_service.answer_question(question)
        # Add background task for evaluation and storage
        background_tasks.add_task(
            evaluation_service.evaluate_and_store, question.question, answer, db
        )
        execution_time = time.time() - start_time
        logger.info("Question answered successfully")

        if wandb_enabled:
            try:
                log_qa_metrics(question, answer, execution_time)
            except Exception as e:
                logger.error(f"Error logging metrics to W&B: {str(e)}")

        return answer
    except Exception as e:
        logger.exception(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An error occurred while processing the question"
        )


@qa_router.get("/metrics", response_model=Dict[str, float])
async def get_metrics(db: Session = Depends(get_db)):
    try:
        logger.info("Retrieving evaluation metrics")

        total_evaluations = db.query(func.count(EvaluationRecord.id)).scalar()
        relevant_evaluations = (
            db.query(func.count(EvaluationRecord.id))
            .filter(EvaluationRecord.relevance == "RELEVANT")
            .scalar()
        )

        hit_rate = (
            relevant_evaluations / total_evaluations if total_evaluations > 0 else 0
        )

        # Calculate MRR
        evaluations = db.query(EvaluationRecord).all()
        reciprocal_ranks = []
        for eval in evaluations:
            if eval.relevance == "RELEVANT":
                reciprocal_ranks.append(1)
            elif eval.relevance == "PARTLY_RELEVANT":
                reciprocal_ranks.append(0.5)
            else:
                reciprocal_ranks.append(0)

        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0

        metrics = {"hit_rate": hit_rate, "mrr": mrr}

        logger.info("Metrics retrieved successfully")
        return metrics
    except Exception as e:
        logger.exception(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An error occurred while retrieving metrics"
        )
