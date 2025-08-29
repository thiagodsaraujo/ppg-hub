from __future__ import annotations
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.repositories.programa_repo import ProgramaRepository
from app.schemas.programa import (
    ProgramaCreate,
    ProgramaUpdate,
    ProgramaRead,
    ProgramaList,
)
from app.models.programa import Programa


class ProgramaService:
    """Camada de regras de negócio para Programas."""

    def __init__(self, db: Session) -> None:
        self.repo = ProgramaRepository(db)

    # ----------------- CREATE -----------------
    def create_programa(self, payload: ProgramaCreate) -> ProgramaRead:
        """
        Cria um novo programa no sistema.
        """
        try:
            programa = self.repo.create(payload.model_dump())
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Violação de unicidade em Programa",
            ) from e
        return ProgramaRead.model_validate(programa)

    # ----------------- READ -----------------
    def get_programa(self, programa_id: int) -> Optional[ProgramaRead]:
        """Obtém um programa pelo ID."""
        programa = self.repo.get(programa_id)
        return ProgramaRead.model_validate(programa) if programa else None

    def list_programas(
        self, limit: int = 50, offset: int = 0
    ) -> Tuple[List[ProgramaRead], int]:
        """Lista programas com paginação."""
        items, total = self.repo.list(limit=limit, offset=offset)
        return [ProgramaRead.model_validate(i) for i in items], total

    def list_all_programas(self) -> List[ProgramaRead]:
        """Lista todos os programas (sem paginação)."""
        items = self.repo.list_all()
        return [ProgramaRead.model_validate(i) for i in items]

    # ----------------- UPDATE -----------------
    def update_programa(self, programa_id: int, payload: ProgramaUpdate) -> Optional[ProgramaRead]:
        """Atualiza um programa existente."""
        data = payload.model_dump(exclude_unset=True)
        programa = self.repo.update(programa_id, data)
        if not programa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Programa não encontrado",
            )
        return ProgramaRead.model_validate(programa)

    # ----------------- DELETE -----------------
    def delete_programa(self, programa_id: int, hard: bool = False) -> bool:
        """Remove um programa do sistema."""
        ok = self.repo.delete(programa_id, hard=hard)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Programa não encontrado",
            )
        return ok
