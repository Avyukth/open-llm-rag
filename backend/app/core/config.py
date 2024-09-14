import os
from typing import Any, Dict

import toml
from pydantic import BaseModel


class ProviderSettings(BaseModel):
    PROVIDER_TYPE: str
    NAME: str
    BASE_URL: str = ""
    API_KEY: str = ""


class LoggingSettings(BaseModel):
    LEVEL: str
    FILE: str
    ROTATION: str
    RETENTION: str


class Settings(BaseModel):
    PROJECT_NAME: str
    UPLOAD_DIR: str
    WEBHOOK_URL: str
    BACKEND_PORT: int
    FRONTEND_PORT: int
    WANDB_API_KEY: str
    LOGGING: LoggingSettings
    LLM: ProviderSettings
    EMBEDDING: ProviderSettings

    @property
    def LOG_LEVEL(self) -> str:
        return self.LOGGING.LEVEL

    @property
    def LOG_FILE(self) -> str:
        return self.LOGGING.FILE

    @property
    def LOG_ROTATION(self) -> str:
        return self.LOGGING.ROTATION

    @property
    def LOG_RETENTION(self) -> str:
        return self.LOGGING.RETENTION


def load_config(config_path: str = "config.toml") -> Settings:
    print(f"Current working directory: {os.getcwd()}")
    print(f"Attempting to load config from: {config_path}")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config_dict = toml.load(f)

    print("Loaded config:")
    print(config_dict)

    llm_config = config_dict["llm"]
    llm_provider = llm_config["PROVIDER"]
    llm_settings = {
        **llm_config["PROVIDERS"][llm_provider],
        "PROVIDER_TYPE": llm_provider,
    }

    embedding_config = config_dict["embedding"]
    embedding_provider = embedding_config["PROVIDER"]
    embedding_settings = {
        **embedding_config["PROVIDERS"][embedding_provider],
        "PROVIDER_TYPE": embedding_provider,
    }

    return Settings(
        PROJECT_NAME=config_dict["general"]["project_name"],
        UPLOAD_DIR=config_dict["general"]["upload_dir"],
        WEBHOOK_URL=config_dict["general"]["webhook_url"],
        BACKEND_PORT=config_dict["general"]["backend_port"],
        FRONTEND_PORT=config_dict["general"]["frontend_port"],
        WANDB_API_KEY=config_dict["wandb"]["wandb_api_key"],
        LOGGING=LoggingSettings(**config_dict["logging"]),
        LLM=ProviderSettings(**llm_settings),
        EMBEDDING=ProviderSettings(**embedding_settings),
    )


settings = load_config()
