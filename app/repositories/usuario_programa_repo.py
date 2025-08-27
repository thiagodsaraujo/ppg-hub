# app/repositories/usuario_programa_repo.py
from __future__ import annotations
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.usuario_programa import UsuarioPrograma

class UsuarioProgramaRepository:
    """Persistência da associação Usuário–Programa."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def vincular(self, data: dict) -> UsuarioPrograma:
        assoc = UsuarioPrograma(**data)
        self.db.add(assoc)
        self.db.flush()
        return assoc

    def listar_membros_do_programa(self, programa_id: int) -> Sequence[UsuarioPrograma]:
        stmt = select(UsuarioPrograma).where(UsuarioPrograma.programa_id == programa_id)
        return self.db.scalars(stmt).all()

    def listar_programas_do_usuario(self, usuario_id: int) -> Sequence[UsuarioPrograma]:
        stmt = select(UsuarioPrograma).where(UsuarioPrograma.usuario_id == usuario_id)
        return self.db.scalars(stmt).all()

    def marcar_inativo(self, assoc_id: int) -> UsuarioPrograma | None:
        assoc = self.db.get(UsuarioPrograma, assoc_id)
        if assoc:
            assoc.ativo = False
        return assoc
