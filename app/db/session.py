from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Engine para o banco Postgres
engine = create_engine(settings.DATABASE_URL, echo=False)

# Factory para criar sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependência padrão para FastAPI (mais comum na comunidade)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Alias para compatibilidade com código legado
get_session = get_db
