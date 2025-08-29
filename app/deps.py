# app/deps.py
from __future__ import annotations
from collections.abc import Generator
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.role_service import RoleService

def get_db() -> Generator[Session, None, None]:
    """Sessão por request: abre/fecha corretamente."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------ Services ------------------
def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    """
    Dependência para injetar RoleService em endpoints.
    Usa o Session fornecido pelo get_db().
    """
    return RoleService(db)

# Alias opcional para código legado
get_session = get_db
