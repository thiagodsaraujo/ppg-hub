from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base

# Engine para o banco Postgres
engine = create_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)

# Factory para criar sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def get_db():
    """Dependência padrão para FastAPI (mais comum na comunidade)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Inicializa schemas e tabelas no banco.
    """
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS core"))

    Base.metadata.create_all(bind=engine)

# Alias para compatibilidade com código legado
get_session = get_db
