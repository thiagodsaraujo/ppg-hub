from __future__ import annotations
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.usuario import Usuario


class UsuarioRepository:
    """Repositório de acesso a dados para Usuários."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ----------------- CREATE -----------------
    def create(self, data: dict) -> Usuario:
        """Cria um usuário no banco de dados."""
        usuario = Usuario(**data)
        self.session.add(usuario)
        self.session.commit()
        self.session.refresh(usuario)
        return usuario

    # ----------------- READ -----------------
    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        """Busca usuário pelo ID."""
        stmt = select(Usuario).where(Usuario.id == usuario_id)
        return self.session.execute(stmt).scalars().first()

    def get_by_email(self, email: str) -> Optional[Usuario]:
        """Busca usuário pelo email."""
        stmt = select(Usuario).where(Usuario.email == email)
        return self.session.execute(stmt).scalars().first()

    def list(self, limit: int = 10, offset: int = 0, ativo: Optional[bool] = None):
        """Lista usuários com paginação e filtro opcional por ativo/inativo."""
        stmt = select(Usuario).offset(offset).limit(limit)
        if ativo is not None:
            stmt = stmt.where(Usuario.ativo == ativo)

        items = self.session.scalars(stmt).all()

        total_stmt = select(func.count()).select_from(Usuario)
        if ativo is not None:
            total_stmt = total_stmt.where(Usuario.ativo == ativo)

        total = self.session.scalar(total_stmt)
        return items, total

    def list_all(self):
        """Lista todos os usuários (sem paginação)."""
        stmt = select(Usuario)
        return self.session.scalars(stmt).all()

    # ----------------- UPDATE -----------------
    def update(self, usuario_id: int, data: dict) -> Optional[Usuario]:
        """Atualiza um usuário."""
        usuario = self.get_by_id(usuario_id)
        if not usuario:
            return None
        for k, v in data.items():
            if hasattr(usuario, k):
                setattr(usuario, k, v)
        self.session.commit()
        self.session.refresh(usuario)
        return usuario

    # ----------------- DELETE -----------------
    def delete(self, usuario_id: int, hard: bool = False) -> bool:
        """Remove usuário do sistema."""
        usuario = self.get_by_id(usuario_id)
        if not usuario:
            return False
        if hard:
            self.session.delete(usuario)
        else:
            usuario.ativo = False
        self.session.commit()
        return True
