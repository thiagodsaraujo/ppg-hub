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
    DocenteRead,
    DocenteList,
)


class DocenteService:
    """Regras de negócio de Docente."""

    def __init__(self, db: Session) -> None:
        # Repositório responsável por falar com o banco
        self.repo = DocenteRepository(db)

    # ---------------------------------------------------
    # CREATE
    # ---------------------------------------------------
    def create_docente(self, payload: DocenteCreate) -> DocenteRead:
        """
        Cria um novo docente.
        - Verifica se já existe vínculo do usuário com o programa.
        - Se sim, lança HTTP 409 (conflito).
        - Se não, cria e retorna o Docente.
        """
        existing = self.repo.list_all()
        for d in existing:
            if d.usuario_id == payload.usuario_id and d.programa_id == payload.programa_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Usuário já está vinculado como docente neste programa.",
                )

        docente = self.repo.create(payload)
        return DocenteRead.model_validate(docente)

    # ---------------------------------------------------
    # GET
    # ---------------------------------------------------
    def get_docente(self, docente_id: int) -> DocenteRead:
        """
        Busca docente pelo ID.
        - Se não encontrado, retorna 404.
        """
        docente = self.repo.get(docente_id)
        if not docente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Docente não encontrado.",
            )
        return DocenteRead.model_validate(docente)

    # ---------------------------------------------------
    # LIST
    # ---------------------------------------------------
    def list_docentes(self, skip: int, limit: int) -> tuple[list[Docente], int]:
        """
        Retorna (items, total) usando paginação offset/limit.
        Define uma ordenação estável (ex.: por id) para consistência.
        """
        stmt_items = (
            select(Docente)
            .order_by(Docente.id.asc())
            .offset(skip)
            .limit(limit)
        )
        items = list(self.db.scalars(stmt_items))

        stmt_total = select(func.count()).select_from(Docente)
        total = self.db.scalar(stmt_total) or 0

        return items, int(total)

    # ---------------------------------------------------
    # UPDATE
    # ---------------------------------------------------
    def update_docente(self, docente_id: int, payload: DocenteUpdate) -> DocenteRead:
        """
        Atualiza docente existente.
        - Se não encontrado, retorna 404.
        - Atualiza apenas campos informados (exclude_unset).
        """
        docente = self.repo.get(docente_id)
        if not docente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Docente não encontrado.",
            )
        docente = self.repo.update(docente, payload)
        return DocenteRead.model_validate(docente)

    # ---------------------------------------------------
    # DELETE
    # ---------------------------------------------------
    def delete_docente(self, docente_id: int) -> None:
        """
        Remove docente do banco.
        - Se não encontrado, retorna 404.
        """
        docente = self.repo.get(docente_id)
        if not docente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Docente não encontrado.",
            )
        self.repo.delete(docente)
