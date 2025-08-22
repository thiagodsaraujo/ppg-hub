"""
Configurações centrais do sistema PPG.

Este módulo centraliza todas as configurações usando Pydantic Settings,
permitindo configuração via variáveis de ambiente ou arquivo .env.
"""

from __future__ import annotations

import os
from typing import Any

from pydantic import Field, PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações principais do sistema.

    Utiliza Pydantic Settings para validação automática e carregamento
    de variáveis de ambiente. Suporta arquivo .env para desenvolvimento.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # === CONFIGURAÇÕES GERAIS ===
    app_name: str = Field(default="PPG System", description="Nome da aplicação")
    version: str = Field(default="0.1.0", description="Versão da aplicação")
    debug: bool = Field(default=False, description="Modo debug")
    environment: str = Field(default="development", description="Ambiente (development/production)")

    # === CONFIGURAÇÕES DO SERVIDOR ===
    host: str = Field(default="0.0.0.0", description="Host do servidor")
    port: int = Field(default=8000, description="Porta do servidor")
    reload: bool = Field(default=True, description="Auto-reload em desenvolvimento")

    # === CONFIGURAÇÕES DO BANCO DE DADOS ===
    # Componentes individuais para flexibilidade
    postgres_user: str = Field(default="postgres", description="Usuário PostgreSQL")
    postgres_password: str = Field(default="postgres", description="Senha PostgreSQL")
    postgres_host: str = Field(default="localhost", description="Host PostgreSQL")
    postgres_port: int = Field(default=5432, description="Porta PostgreSQL")
    postgres_db: str = Field(default="ppg_system", description="Nome do banco")

    # DSN completa (construída automaticamente)
    database_url: PostgresDsn | None = Field(default=None, description="URL completa do banco")

    # Pool de conexões
    db_pool_size: int = Field(default=5, description="Tamanho do pool de conexões")
    db_max_overflow: int = Field(default=10, description="Máximo overflow do pool")
    db_pool_timeout: int = Field(default=30, description="Timeout do pool (segundos)")
    db_echo: bool = Field(default=False, description="Echo SQL queries (debug)")

    # === CONFIGURAÇÕES DE SEGURANÇA ===
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Chave secreta para JWT"
    )
    algorithm: str = Field(default="HS256", description="Algoritmo para JWT")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Expiração do token de acesso (minutos)"
    )

    # === CONFIGURAÇÕES DE CORS ===
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Origins permitidas para CORS"
    )

    # === CONFIGURAÇÕES DE LOGGING ===
    log_level: str = Field(default="INFO", description="Nível de log")
    log_format: str = Field(default="json", description="Formato do log (json/plain)")
    log_file: str | None = Field(default=None, description="Arquivo de log (opcional)")

    @validator("database_url", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> str:
        """
        Constrói a URL do banco a partir dos componentes individuais.

        Se database_url não for fornecida, monta a partir dos componentes
        postgres_user, postgres_password, postgres_host, etc.
        """
        if isinstance(v, str):
            return v

        # Monta a DSN a partir dos componentes
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("postgres_user"),
            password=values.get("postgres_password"),
            host=values.get("postgres_host"),
            port=values.get("postgres_port"),
            path=f"/{values.get('postgres_db') or ''}",
        )

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """
        Converte string separada por vírgulas em lista.

        Permite configurar CORS_ORIGINS como "http://localhost:3000,http://localhost:8080"
        ou como lista diretamente.
        """
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def sqlalchemy_database_uri(self) -> str:
        """
        Retorna a URI do SQLAlchemy.

        Converte de postgresql:// para postgresql+psycopg2:// se necessário.
        """
        uri = str(self.database_url)
        if uri.startswith("postgresql://"):
            uri = uri.replace("postgresql://", "postgresql+psycopg2://", 1)
        return uri

    @property
    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento."""
        return self.environment.lower() in ("development", "dev", "local")

    @property
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção."""
        return self.environment.lower() in ("production", "prod")


# Instância global das configurações
# Carregada uma vez na inicialização da aplicação
settings = Settings()


def get_settings() -> Settings:
    """
    Retorna as configurações do sistema.

    Função para uso com FastAPI Depends(), permitindo
    override em testes e injeção de dependência.

    Returns:
        Settings: Configurações carregadas

    Example:
        ```python
        from fastapi import Depends

        def my_endpoint(settings: Settings = Depends(get_settings)):
            database_url = settings.sqlalchemy_database_uri
        ```
    """
    return settings


# Exemplo de arquivo .env para desenvolvimento
ENV_EXAMPLE = """
# === CONFIGURAÇÕES GERAIS ===
APP_NAME=PPG System
VERSION=0.1.0
DEBUG=true
ENVIRONMENT=development

# === CONFIGURAÇÕES DO SERVIDOR ===
HOST=0.0.0.0
PORT=8000
RELOAD=true

# === CONFIGURAÇÕES DO BANCO ===
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ppg_system

# === CONFIGURAÇÕES DE SEGURANÇA ===
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# === CONFIGURAÇÕES DE CORS ===
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# === CONFIGURAÇÕES DE LOGGING ===
LOG_LEVEL=INFO
LOG_FORMAT=json
"""

if __name__ == "__main__":
    # Script para gerar arquivo .env de exemplo
    print("=== CONFIGURAÇÕES CARREGADAS ===")
    config = Settings()
    print(f"App Name: {config.app_name}")
    print(f"Environment: {config.environment}")
    print(f"Database URL: {config.sqlalchemy_database_uri}")
    print(f"Debug Mode: {config.debug}")

    # Criar .env se não existir
    if not os.path.exists(".env"):
        print("\n=== CRIANDO ARQUIVO .env ===")
        with open(".env", "w") as f:
            f.write(ENV_EXAMPLE)
        print("Arquivo .env criado! Edite conforme necessário.")