# app/deps.py
from collections.abc import Generator
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.session import SessionLocal
from app.services.role_service import RoleService

def get_db() -> Generator[Session, None, None]:
    """Sessão por request: abre/fecha corretamente."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    return RoleService(db)

# alias para compatibilidade
get_session = get_db
