# app/repositories/docente_repo.py
from typing import Mapping, Any

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.docente import Docente

class DocenteRepository:
    """Persistência de Docente."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: dict) -> Docente:
        docente = Docente(**payload)
        self.db.add(docente)
        self.db.flush()
        return docente

    def get(self, docente_id: int) -> Docente | None:
        return self.db.get(Docente, docente_id)

    def list(self, skip: int = 0, limit: int = 10) -> list[Docente]:
        stmt = select(Docente).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def count(self) -> int:
        stmt = select(func.count()).select_from(Docente)
        return self.db.scalar(stmt)

    def update_fields(self, docente: Docente, fields: Mapping[str, Any]) -> Docente:
        for k, v in fields.items():
            setattr(docente, k, v)
        self.db.add(docente)
        self.db.commit()
        self.db.refresh(docente)
        return docente

    def delete(self, docente_id: int) -> bool:
        docente = self.get(docente_id)
        if not docente:
            return False
        self.db.delete(docente)
        return True
