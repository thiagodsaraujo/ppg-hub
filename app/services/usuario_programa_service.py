# app/services/usuario_programa_service.py
from __future__ import annotations
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.repositories.usuario_programa_repo import UsuarioProgramaRepository
from app.schemas.usuario_programa import VincularUsuarioProgramaIn
from app.models.usuario_programa import UsuarioPrograma
from app.deps import get_db


class UsuarioProgramaService:
    """Regras para vínculo usuário–programa."""

    def __init__(self, db: Session) -> None:
        self.repo = UsuarioProgramaRepository(db)

    def vincular(self, programa_id: int, payload: VincularUsuarioProgramaIn) -> UsuarioPrograma:
        data = payload.model_dump()
        data["programa_id"] = programa_id
        try:
            return self.repo.vincular(data)
        except IntegrityError as exc:
            # Transforme em erro de domínio; o router traduz em HTTP 409
            raise ValueError("Usuário já vinculado a este programa.") from exc

    def desativar(self, assoc_id: int) -> UsuarioPrograma | None:
        return self.repo.marcar_inativo(assoc_id)
