# app/services/instituicao_service.py
from __future__ import annotations
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.deps import get_db


from app.schemas.instituicao import InstituicaoUpdate, InstituicaoRead, InstituicaoPut
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

    def put(self, instituicao_id: int, payload: InstituicaoPut) -> InstituicaoRead:
        obj = self.repo.get(instituicao_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Instituição não encontrada")

        data = payload.model_dump()  # PUT = payload completo
        # regra opcional: impedir mudança de 'codigo'
        data.pop("codigo", None)

        self.repo.update_fields(obj, data)  # aplica campos
        try:
            self.repo.db.commit()  # PERSISTE
        except IntegrityError as e:
            self.repo.db.rollback()
            raise  # handler global devolve 409
        self.repo.db.refresh(obj)  # RECARREGA (defaults/onupdate)

        return InstituicaoRead.model_validate(obj)

    def patch(self, instituicao_id: int, payload: InstituicaoUpdate) -> InstituicaoRead:
        obj = self.repo.get(instituicao_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Instituição não encontrada")
        changes = payload.model_dump(exclude_unset=True)
        try:
            self.repo.update_partial(obj, changes)
            self.repo.db.commit()
        except IntegrityError as e:
            self.repo.db.rollback()
            raise HTTPException(status_code=409, detail="Violação de integridade (sigla/código únicos).") from e
        self.repo.db.refresh(obj)
        return InstituicaoRead.model_validate(obj)