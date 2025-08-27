# app/repositories/programa_repo.py
from __future__ import annotations
from typing import Sequence, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.programa import Programa

class ProgramaRepository:
    """Operações de persistência para Programa."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: dict) -> Programa:
        obj = Programa(**data)
        self.db.add(obj)
        self.db.flush()  # gera id
        return obj

    def get(self, programa_id: int) -> Optional[Programa]:
        return self.db.get(Programa, programa_id)

    def list(self, limit: int = 50, offset: int = 0) -> Sequence[Programa]:
        stmt = select(Programa).limit(limit).offset(offset)
        return self.db.scalars(stmt).all()
