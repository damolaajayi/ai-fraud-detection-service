from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "ai-fraud-detection-service"
    environment: str = "development"
    debug: bool = True

    database_url: str
    redis_url: str

    model_path: str = "models/fraud_model_v1.pkl"
    active_model_version: str = "fraud-model-v1.0.0"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()