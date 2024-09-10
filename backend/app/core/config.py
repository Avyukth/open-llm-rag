from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Document QA API"
    MODEL_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OPENAI_API_KEY: str = ""
    COHERE_API_KEY: str = ""
    UPLOAD_DIR: str = "./uploads"
    WEBHOOK_URL: str = "http://localhost:8501/webhook"
    MODEL_NAME: str = "llama3.1:8b"

    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 8501
    OLLAMA_PORT: int = 11434

    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    LOG_ROTATION: str = "500 MB"
    LOG_RETENTION: str = "10 days"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
