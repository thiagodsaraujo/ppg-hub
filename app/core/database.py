"""
Configuração do banco de dados com SQLAlchemy 2.x.

Este módulo configura a engine, sessions e base declarativa
seguindo as melhores práticas do SQLAlchemy 2.0+.
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine, event, pool
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

# Logger estruturado
logger = logging.getLogger(__name__)

# === BASE DECLARATIVA ===
# Classe base para todos os modelos SQLAlchemy
Base = declarative_base()

# === CONFIGURAÇÃO DA ENGINE ===
settings = get_settings()

# Engine principal para produção
engine = create_engine(
    settings.sqlalchemy_database_uri,
    # Pool de conexões otimizado
    poolclass=pool.QueuePool,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=3600,  # Recicla conexões a cada hora
    pool_pre_ping=True,  # Verifica conexões antes de usar
    # Echo SQL em desenvolvimento
    echo=settings.db_echo,
    # Configurações de performance
    execution_options={
        "isolation_level": "READ_COMMITTED"
    }
)

# Session factory configurada
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,  # SQLAlchemy 2.x padrão
    autoflush=False,  # Controle manual de flush
    expire_on_commit=False  # Permite acesso após commit
)


# === EVENTOS PARA LOGGING ===
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record) -> None:
    """
    Configura pragmas específicos para SQLite em testes.

    Args:
        dbapi_connection: Conexão DBAPI
        connection_record: Record da conexão
    """
    if "sqlite" in str(engine.url):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany) -> None:
    """
    Loga queries SQL em modo debug.

    Args:
        conn: Conexão
        cursor: Cursor
        statement: Statement SQL
        parameters: Parâmetros
        context: Contexto de execução
        executemany: Se é executemany
    """
    if settings.debug:
        logger.debug(
            "Executing SQL",
            extra={
                "sql_statement": statement,
                "sql_parameters": parameters,
                "execute_many": executemany
            }
        )


# === DEPENDENCY PARA FASTAPI ===
def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter sessão do banco de dados no FastAPI.

    Segue o padrão de context manager para garantir que a sessão
    seja sempre fechada, mesmo em caso de exceção.

    Yields:
        Session: Sessão do SQLAlchemy configurada

    Example:
        ```python
        from fastapi import Depends
        from sqlalchemy.orm import Session

        def my_endpoint(db: Session = Depends(get_db)):
            # Usar db para queries
            pass
        ```
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        logger.debug("Database session closed")
        db.close()


# === FUNÇÕES UTILITÁRIAS ===
def create_tables() -> None:
    """
    Cria todas as tabelas definidas nos modelos.

    ATENÇÃO: Use apenas em desenvolvimento/testes.
    Em produção, sempre use Alembic para migrações.
    """
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_tables() -> None:
    """
    Remove todas as tabelas do banco.

    ATENÇÃO: Operação destrutiva! Use apenas em testes.
    """
    logger.warning("Dropping all database tables")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")


def check_connection() -> bool:
    """
    Verifica se a conexão com o banco está funcionando.

    Returns:
        bool: True se conexão OK, False caso contrário

    Example:
        ```python
        if not check_connection():
            logger.error("Database connection failed")
            sys.exit(1)
        ```
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


# === CONFIGURAÇÃO PARA TESTES ===
def create_test_engine(database_url: str = "sqlite:///./test.db") -> Engine:
    """
    Cria engine específica para testes.

    Usa SQLite em memória ou arquivo temporário para testes
    rápidos e isolados.

    Args:
        database_url: URL do banco de teste

    Returns:
        Engine: Engine configurada para testes

    Example:
        ```python
        # Em conftest.py
        test_engine = create_test_engine("sqlite:///:memory:")
        TestingSessionLocal = sessionmaker(bind=test_engine)
        ```
    """
    test_engine = create_engine(
        database_url,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False  # Apenas para SQLite
        } if "sqlite" in database_url else {},
        echo=False  # Reduz logs em testes
    )
    return test_engine


class DatabaseManager:
    """
    Gerenciador de contexto para operações de banco.

    Facilita operações transacionais com commit/rollback automático.
    Útil para operações que precisam de controle transacional explícito.
    """

    def __init__(self, session: Session | None = None):
        """
        Inicializa o gerenciador.

        Args:
            session: Sessão existente ou None para criar nova
        """
        self._session = session
        self._should_close = session is None

    def __enter__(self) -> Session:
        """
        Entrada do context manager.

        Returns:
            Session: Sessão configurada
        """
        if self._session is None:
            self._session = SessionLocal()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Saída do context manager com controle transacional.

        Args:
            exc_type: Tipo da exceção (se houver)
            exc_val: Valor da exceção
            exc_tb: Traceback da exceção
        """
        if exc_type is not None:
            # Houve exceção - fazer rollback
            logger.error(f"Transaction rolled back due to error: {exc_val}")
            self._session.rollback()
        else:
            # Sucesso - fazer commit
            logger.debug("Transaction committed successfully")
            self._session.commit()

        # Fechar sessão se criada pelo manager
        if self._should_close and self._session:
            self._session.close()


# === INICIALIZAÇÃO ===
def init_database() -> None:
    """
    Inicializa o banco de dados.

    Verifica conexão e registra informações básicas.
    Deve ser chamada na inicialização da aplicação.
    """
    logger.info("Initializing database connection")

    if not check_connection():
        raise Exception("Failed to connect to database")

    logger.info(
        "Database initialized successfully",
        extra={
            "database_url": str(engine.url).split("@")[-1],  # Remove credenciais do log
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow
        }
    )


if __name__ == "__main__":
    # Script para testar configuração do banco
    import sys

    print("=== TESTE DE CONEXÃO COM BANCO ===")

    try:
        init_database()
        print("✅ Conexão com banco de dados OK")

        # Teste de sessão
        with DatabaseManager() as db:
            result = db.execute("SELECT 1 as test").fetchone()
            print(f"✅ Teste de query OK: {result}")

    except Exception as e:
        print(f"❌ Erro na configuração do banco: {e}")
        sys.exit(1)