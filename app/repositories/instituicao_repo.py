# app/repositories/instituicao_repo.py
from __future__ import annotations  # <- evita avaliar tipos em runtime
from collections.abc import Mapping  # <- preferível em 3.9+
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.instituicao import Instituicao


class InstituicaoRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Instituicao:
        obj = Instituicao(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get(self, instituicao_id: int) -> Instituicao | None:
        return self.db.get(Instituicao, instituicao_id)

    def list(self, limit: int = 10, offset: int = 0) -> tuple[list[Instituicao], int]:
        stmt = select(Instituicao).offset(offset).limit(limit)
        items = self.db.scalars(stmt).all()
        total = self.db.scalar(select(func.count()).select_from(Instituicao))
        return items, total

    # def update(self, instituicao_id: int, data: dict) -> Instituicao | None:
    #     obj = self.get(instituicao_id)
    #     if not obj:
    #         return None
    #     for k, v in data.items():
    #         setattr(obj, k, v)
    #     self.db.add(obj)
    #     self.db.commit()
    #     self.db.refresh(obj)
    #     return obj

    def update_replace(self, obj: Instituicao, data: Mapping[str, Any]) -> Instituicao:
        """PUT: substitui campos do recurso por data completa (validada no schema Put)."""
        # Se 'codigo' for imutável no seu domínio, remova:
        # data = {k: v for k, v in data.items() if k != "codigo"}
        for field, value in data.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        self.db.add(obj)
        return obj


    def update_partial(self, obj: Instituicao, data: Mapping[str, Any]) -> Instituicao:
        """Atualiza somente campos presentes (PATCH)."""
        for field, value in data.items():
            # ignorar chaves não mapeadas
            if not hasattr(obj, field):
                continue
            setattr(obj, field, value)
        self.db.add(obj)  # anexa à sessão se for transiente
        return obj

    def delete(self, instituicao_id: int) -> bool:
        obj = self.get(instituicao_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
