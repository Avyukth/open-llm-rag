import os

import wandb
import weave
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger()


def init_wandb():
    try:
        wandb_api_key = settings.WANDB_API_KEY
        if not wandb_api_key:
            logger.warning(
                "WANDB_API_KEY not found in environment variables. W&B logging will be disabled."
            )
            return False

        wandb.login(key=wandb_api_key)
        wandb.init(
            project=settings.PROJECT_NAME,
            config={
                "llm_provider": settings.LLM.PROVIDER_TYPE,
                "embedding_provider": settings.EMBEDDING.PROVIDER_TYPE,
                "log_level": settings.LOG_LEVEL,
            },
        )
        weave.init(settings.PROJECT_NAME)
        logger.info("W&B initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize W&B: {str(e)}")
        return False


def log_qa_metrics(question, answer, execution_time):
    if wandb.run is not None:
        wandb.log(
            {
                "question_length": len(
                    question.question
                ),  # Changed from question.text to question.question
                "answer_length": len(answer.answer),
                "execution_time": execution_time,
                "num_sources": len(
                    answer.sources
                ),  # Added logging for number of sources
            }
        )
    else:
        logger.debug("W&B run not initialized. Skipping metric logging.")


def finish_wandb():
    if wandb.run is not None:
        wandb.finish()
        logger.info("W&B run finished")
    else:
        logger.debug("No active W&B run to finish")
