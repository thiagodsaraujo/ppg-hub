# app/repositories/usuario_programa_role_repo.py

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.usuario_programa_role import UsuarioProgramaRole

class UsuarioProgramaRoleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_usuario_programa(self, usuario_id: int, programa_id: int) -> UsuarioProgramaRole | None:
        stmt = select(UsuarioProgramaRole).where(
            UsuarioProgramaRole.usuario_id == usuario_id,
            UsuarioProgramaRole.programa_id == programa_id,
            UsuarioProgramaRole.status == "Ativo"
        )
        return self.session.scalar(stmt)
