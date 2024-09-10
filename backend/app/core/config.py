from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Document QA API"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    UPLOAD_DIR: str = "./uploads"
    WEBHOOK_URL: str = "http://localhost:8501/webhook"
    MODEL: str = "llama3.1:8b"
    
    # Add these new fields
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 8501
    OLLAMA_PORT: int = 11434

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
