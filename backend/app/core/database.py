import os

from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure the database directory exists
db_dir = os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", ""))
os.makedirs(db_dir, exist_ok=True)

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create the engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
