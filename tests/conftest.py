from __future__ import annotations
import os
import sys
import importlib
import urllib.parse
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# 1) Garanta que a raiz do projeto está no PYTHONPATH
#    (roda 'pytest' a partir da raiz; isto é só um fallback)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT_CANDIDATE = os.path.abspath(os.path.join(PROJECT_ROOT, ".."))
if ROOT_CANDIDATE not in sys.path:
    sys.path.insert(0, ROOT_CANDIDATE)

from app.db.base import Base  # Base declarative comum a todos os modelos

# ==========================
# Config DB (dados reais)
# ==========================
DB_HOST = os.getenv("DB_HOST", "148.230.76.86")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "ppghub_dev")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv(
    "DB_PASS",
    "NIgBA3LQgmXTanJ8GjDewwOob5vxk8yJLkPgv1pa823mHhM9ovbtKFh4qMUP8WpF",
)
ENC_PASS = urllib.parse.quote_plus(DB_PASS)
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{ENC_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def import_models() -> None:
    """
    Importa explicitamente todos os módulos de modelos para popular Base.metadata.
    Ajuste a lista conforme você cria novos arquivos em app/models/.
    """
    modules = [
        "app.models.instituicao",
        # adicione aqui: "app.models.programa",
        # "app.models.discente", "app.models.docente", "app.models.trabalho_conclusao",
        # "app.models.banca", "app.models.usuario", "app.models.role", etc.
    ]
    for mod in modules:
        try:
            importlib.import_module(mod)
        except ModuleNotFoundError as e:
            print(f"[WARN] Módulo não encontrado (ok se ainda não existe): {mod} -> {e}")


def ensure_schemas(conn) -> None:
    """
    Cria schemas necessários no banco real. Ajuste conforme seu desenho atual.
    """
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS core"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS academic"))
    # Se seus modelos usam schema="core"/"auth"/"academic", eles precisam existir.


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    - Valida conexão
    - Cria schemas (core/auth/academic)
    - Importa modelos -> popula Base.metadata
    - Cria tabelas no banco real (populate)
    """
    print(f"[PPGHUB] Conectando ao banco real: {DATABASE_URL}")
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ Conexão OK.")

    # 1) Cria schemas
    with engine.begin() as conn:
        ensure_schemas(conn)

    # 2) Importa modelos para encher o metadata
    import_models()

    # 3) Debug: quantas tabelas o SQLAlchemy "enxerga"?
    table_count = len(Base.metadata.tables)
    print(f"🔎 Base.metadata.tables: {table_count} tabela(s) registradas.")
    if table_count == 0:
        print("⚠️ Nenhuma tabela registrada no metadata. "
              "Verifique se você importou os modelos (app.models.*) corretamente "
              "e se eles estão declarados com o mesmo Base.")

    # 4) Cria tabelas
    with engine.begin() as conn:
        Base.metadata.create_all(bind=conn)
    print("🛠️  create_all() executado.")

    yield
    # populate-only: não derrubamos nada no final


@pytest.fixture()
def db_session() -> Session:
    """
    Sessão real com commit automático -> grava de verdade no banco.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session):
    """
    TestClient usando a sessão real (sem override obrigatório).
    Se existir um get_db/get_session, faremos override; senão, só devolvemos o client.
    """
    from fastapi.testclient import TestClient
    from app.main import app

    dep = None
    # tente localizar sua dependência de sessão; se não existir, segue sem override
    try:
        from app.deps import get_db as dep  # app/deps.py
    except Exception:
        try:
            from app.api.deps import get_db as dep  # app/api/deps.py
        except Exception:
            try:
                from app.db.session import get_session as dep  # padrão comum
            except Exception:
                dep = None

    if dep is not None:
        def override():
            yield db_session
        app.dependency_overrides[dep] = override

    return TestClient(app)

# dentro do seu conftest atual (que já te passei):
def import_models() -> None:
    import importlib
    modules = [
        "app.models.role",
        "app.models.instituicao",  # adicione aqui todos os outros modelos reais
        # "app.models.usuario",
        # "app.models.programa",
        # ...
    ]
    for m in modules:
        try:
            importlib.import_module(m)
        except Exception as e:
            print(f"[WARN] Falha importando {m}: {e}")
