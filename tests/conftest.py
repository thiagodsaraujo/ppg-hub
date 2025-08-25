from __future__ import annotations

import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_session


@pytest.fixture(scope="session")
def db_url() -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    return f"sqlite:///{tmp.name}"


@pytest.fixture(scope="session")
def test_engine(db_url: str):
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine):
    TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_session():
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
