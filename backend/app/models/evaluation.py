# app/models/evaluation.py
import hashlib

from app.core.database import engine
from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class EvaluationRecord(Base):
    __tablename__ = "evaluations"

    id = Column(String(32), primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(Text, nullable=False)
    relevance = Column(String(20), nullable=False)
    explanation = Column(Text, nullable=False)  # Added explanation column

    @classmethod
    def create_id(cls, question: str) -> str:
        return hashlib.md5(question.encode()).hexdigest()


# Create the table
Base.metadata.create_all(bind=engine)
