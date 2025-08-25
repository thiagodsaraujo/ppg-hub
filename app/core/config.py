from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Configurações globais da aplicação (carrega de variáveis de ambiente e .env)."""

    # Requeridas em produção:
    DATABASE_URL: str        # ex: postgresql+psycopg://user:pass@host:5433/ppg_hub
    SECRET_KEY: str          # usada no JWT

    # Opcionais:
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # ⚙️ Diz ao pydantic-settings para ler o arquivo .env na raiz do projeto
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",      # ignora chaves extras no .env
    )

# Instância única usada pelo app
settings = Settings()
