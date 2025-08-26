# app/repositories/role_repo.py
from __future__ import annotations

from typing import Optional, Tuple, Iterable, List
from sqlalchemy import select, func, update as sa_update, delete as sa_delete
from sqlalchemy.orm import Session

from app.models.role import Role  # deve mapear para schema auth.roles (tabela já existente)


class RoleRepository:
    """Acesso a dados para o agregado Role (RBAC).

    Métodos expostos:
      - create(data) -> Role
      - get_by_id(role_id) -> Optional[Role]
      - get_by_nome(nome) -> Optional[Role]
      - list(limit, offset, search, ativo) -> Tuple[list[Role], int]
      - update(role_id, data) -> Role
      - delete(role_id, hard=False) -> None
    """

    def __init__(self, session: Session) -> None:
        """Inicializa o repositório.

        Args:
            session: Sessão SQLAlchemy já configurada.
        """
        self.session: Session = session

    # ----------------- CREATE -----------------
    def create(self, data: dict) -> Role:
        """Cria e persiste uma Role.

        Args:
            data: Dicionário com campos compatíveis com o modelo Role.

        Returns:
            Role persistida (com ID).
        """
        role = Role(**data)  # type: ignore[arg-type]
        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)
        return role

    # ----------------- READ -------------------
    def get_by_id(self, role_id: int) -> Optional[Role]:
        """Busca Role por ID."""
        stmt = select(Role).where(Role.id == role_id)
        return self.session.execute(stmt).scalars().first()

    def get_by_nome(self, nome: str) -> Optional[Role]:
        """Busca Role por nome exato (UNIQUE)."""
        stmt = select(Role).where(Role.nome == nome)
        return self.session.execute(stmt).scalars().first()

    def list(
        self,
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None,
        ativo: Optional[bool] = None,
    ) -> Tuple[list[Role], int]:
        """Lista roles paginadas com filtros opcionais.

        Args:
            limit: Tamanho da página.
            offset: Deslocamento.
            search: Filtro de nome (ilike '%search%').
            ativo: Filtra por status ativo/inativo.

        Returns:
            (items, total)
        """
        stmt = select(Role)
        if search:
            stmt = stmt.where(Role.nome.ilike(f"%{search}%"))
        if ativo is not None:
            stmt = stmt.where(Role.ativo.is_(ativo))

        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.session.execute(total_stmt).scalar_one()

        stmt = stmt.order_by(Role.id.desc()).limit(limit).offset(offset)
        items = list(self.session.execute(stmt).scalars().all())
        return items, int(total)

    # ----------------- UPDATE -----------------
    def update(self, role_id: int, data: dict) -> Role:
        """Atualiza campos parciais da Role."""
        # alternativa 1: carregar e setar atributos
        role = self.get_by_id(role_id)
        if not role:
            raise ValueError("Role não encontrada")

        for k, v in data.items():
            if hasattr(role, k):
                setattr(role, k, v)

        self.session.commit()
        self.session.refresh(role)
        return role

    def list_all(self) -> List[Role]:
        """Retorna todas as Roles, ordenadas por nome (resultado previsível)."""
        stmt = select(Role).order_by(Role.nome)
        return list(self.session.execute(stmt).scalars().all())

    # ----------------- DELETE -----------------
    def delete(self, role_id: int, hard: bool = False) -> None:
        """Remove Role.

        Args:
            role_id: ID
            hard: Se True, exclui de vez (DELETE). Senão, faz soft delete (ativo=False).
        """
        if hard:
            self.session.execute(sa_delete(Role).where(Role.id == role_id))
        else:
            self.session.execute(
                sa_update(Role).where(Role.id == role_id).values(ativo=False)
            )
        self.session.commit()
