from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderSettings(BaseSettings):
    provider_type: str
    name: str
    base_url: str = ""
    api_key: str = ""


class Settings(BaseSettings):
    PROJECT_NAME: str = "Document QA API"
    UPLOAD_DIR: str = "./../uploads"
    WEBHOOK_URL: str = "http://frontend:8501/webhook"

    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 8501
    OLLAMA_PORT: int = 11434
    OLLAMA_BASE_URL: str = "http://ollama:11434"

    # LLM and Embedding settings
    LLM: ProviderSettings = ProviderSettings(
        provider_type="ollama", name="llama3.1:8b", base_url=OLLAMA_BASE_URL
    )
    EMBEDDING: ProviderSettings = ProviderSettings(
        provider_type="ollama", name="llama3.1:8b", base_url=OLLAMA_BASE_URL
    )

    # Provider-specific API keys
    OPENAI_API_KEY: str = ""
    COHERE_API_KEY: str = ""

    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    LOG_ROTATION: str = "500 MB"
    LOG_RETENTION: str = "10 days"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
