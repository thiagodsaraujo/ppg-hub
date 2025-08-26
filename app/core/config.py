from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str        # URL do banco
    SECRET_KEY: str          # usada no JWT
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, staging, production

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
