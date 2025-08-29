# app/services/programa_service.py
from __future__ import annotations
from sqlalchemy.orm import Session
from app.repositories.programa_repo import ProgramaRepository
from app.schemas.programa import ProgramaCreate
from app.models.programa import Programa
from app.deps import get_db


class ProgramaService:
    """Regras de negócio de Programa."""

    def __init__(self, db: Session) -> None:
        self.repo = ProgramaRepository(db)

    def criar(self, payload: ProgramaCreate) -> Programa:
        # Aqui você pode validar unicidade (instituicao_id + sigla) se quiser antes de persistir.
        return self.repo.create(payload.model_dump())
