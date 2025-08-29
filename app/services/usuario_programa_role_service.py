# app/services/usuario_programa_role_service.py

from sqlalchemy.orm import Session
from app.repositories.usuario_programa_role_repo import UsuarioProgramaRoleRepository
from fastapi import HTTPException, status
from datetime import date

class UsuarioProgramaRoleService:
    def __init__(self, db: Session):
        self.repo = UsuarioProgramaRoleRepository(db)

    def desvincular_usuario_programa(self, usuario_id: int, programa_id: int) -> bool:
        vinculo = self.repo.get_by_usuario_programa(usuario_id, programa_id)
        if not vinculo:
            return False
        vinculo.status = "Desligado"
        vinculo.data_desvinculacao = date.today()
        self.repo.session.commit()
        return True
