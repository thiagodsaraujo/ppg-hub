# app/services/docente_service.py
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.repositories.docente_repo import DocenteRepository
from app.models.docente import Docente
from app.schemas.docente import (
    DocenteCreate,
    DocenteUpdate,
    DocentePatch,
    DocenteRead,
)

class DocenteService:
    """Regras de negócio de Docente."""

    def __init__(self, db: Session) -> None:
        self.db = db                     # ✅ usado em list_docentes (se houver)
        self.repo = DocenteRepository(db)

    # ----------------- CREATE -----------------
    def create_docente(self, payload: DocenteCreate) -> DocenteRead:
        # ... (seu código existente) ...
        docente = self.repo.create(payload)
        return DocenteRead.model_validate(docente)

    # ----------------- GET -----------------
    def get_docente(self, docente_id: int) -> DocenteRead:
        docente = self.repo.get(docente_id)
        if not docente:
            raise HTTPException(status_code=404, detail="Docente não encontrado.")
        return DocenteRead.model_validate(docente)

    # ----------------- LIST -----------------
    def list_docentes(self, skip: int, limit: int) -> tuple[list[Docente], int]:
        # ... (se já tiver, mantenha) ...
        stmt_total = select(func.count()).select_from(Docente)
        total = self.db.scalar(stmt_total) or 0
        stmt_items = select(Docente).order_by(Docente.id.asc()).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt_items))
        return items, int(total)

    # ----------------- PUT (atualização “merge”) -----------------
    def update_docente(self, docente_id: int, payload: DocenteUpdate) -> DocenteRead:
        """
        PUT com semântica prática: aplica somente os campos enviados (merge).
        Se quiser semântica FULL, torne campos obrigatórios em DocenteUpdate.
        """
        docente = self.repo.get(docente_id)
        if not docente:
            raise HTTPException(status_code=404, detail="Docente não encontrado.")
        fields = payload.model_dump(exclude_unset=True)  # 👈 tri-estado controlado no PATCH
        if not fields:
            return DocenteRead.model_validate(docente)
        docente = self.repo.update_fields(docente, fields)
        return DocenteRead.model_validate(docente)

    # ----------------- PATCH (merge-patch RFC 7396) -----------------
    def patch_docente(self, docente_id: int, payload: DocentePatch) -> DocenteRead:
        """
        PATCH merge-patch:
        - campo ausente: não altera
        - presente com null: seta NULL (se coluna permitir)
        - presente com valor: atualiza
        """
        docente = self.repo.get(docente_id)
        if not docente:
            raise HTTPException(status_code=404, detail="Docente não encontrado.")
        fields = payload.model_dump(exclude_unset=True)  # ⛔ NÃO use exclude_none aqui
        if not fields:
            return DocenteRead.model_validate(docente)
        docente = self.repo.update_fields(docente, fields)
        return DocenteRead.model_validate(docente)

    # ----------------- DELETE -----------------
    def delete_docente(self, docente_id: int) -> None:
        docente = self.repo.get(docente_id)
        if not docente:
            raise HTTPException(status_code=404, detail="Docente não encontrado.")
        self.repo.delete(docente)
