# app/services/instituicao_service.py
from __future__ import annotations
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.instituicao import InstituicaoUpdate, InstituicaoRead
from app.repositories.instituicao_repo import InstituicaoRepository


class InstituicaoService:

    def __init__(self, db: Session):
        self.repo = InstituicaoRepository(db)

    def create(self, data: dict):
        return self.repo.create(data)

    def list(self, limit: int, offset: int):
        return self.repo.list(limit, offset)

    def get(self, instituicao_id: int):
        return self.repo.get(instituicao_id)

    def update(self, instituicao_id: int, data: dict):
        return self.repo.update(instituicao_id, data)

    def delete(self, instituicao_id: int):
        return self.repo.delete(instituicao_id)

    def patch(self, instituicao_id: int, payload: InstituicaoUpdate) -> InstituicaoRead:
        obj = self.repo.get(instituicao_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Instituição não encontrada")

        # Converte somente campos enviados (Swagger: “application/json”)
        changes = payload.model_dump(exclude_unset=True)

        # Regra opcional: não permitir alteração de 'codigo' por aqui
        changes.pop("codigo", None)

        self.repo.update_partial(obj, changes)
        try:
            self.repo.db.commit()  # >>> sem commit não persiste
        except IntegrityError as e:
            self.repo.db.rollback()
            # Ex.: conflito de 'sigla' única
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Violação de integridade (ex.: sigla/código já existe)",
            ) from e

        self.repo.db.refresh(obj)
        return InstituicaoRead.model_validate(obj)
