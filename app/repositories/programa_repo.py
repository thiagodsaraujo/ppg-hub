from __future__ import annotations
from typing import Optional, Tuple, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.programa import Programa


class ProgramaRepository:
    """Repositório de acesso a dados para Programas."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ----------------- CREATE -----------------
    def create(self, data: dict) -> Programa:
        """Cria um novo programa."""
        obj = Programa(**data)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    # ----------------- READ -----------------
    def get(self, programa_id: int) -> Optional[Programa]:
        """Busca programa por ID."""
        return self.session.get(Programa, programa_id)

    def list(self, limit: int = 50, offset: int = 0) -> Tuple[List[Programa], int]:
        """
        Lista programas com paginação.
        Retorna (items, total).
        """
        stmt = select(Programa).offset(offset).limit(limit)
        items = self.session.scalars(stmt).all()

        total = self.session.scalar(select(func.count()).select_from(Programa))
        return items, total

    def list_all(self) -> List[Programa]:
        """Lista todos os programas sem paginação."""
        stmt = select(Programa)
        return self.session.scalars(stmt).all()

    # ----------------- UPDATE -----------------
    def update(self, programa_id: int, data: dict) -> Optional[Programa]:
        """Atualiza dados de um programa existente."""
        obj = self.get(programa_id)
        if not obj:
            return None
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    # ----------------- DELETE -----------------
    def delete(self, programa_id: int, hard: bool = False) -> bool:
        """
        Remove um programa.
        - hard=True → exclusão física
        - hard=False → soft delete (status='Inativo'), se o modelo tiver esse campo
        """
        obj = self.get(programa_id)
        if not obj:
            return False

        if hard or not hasattr(obj, "ativo"):
            self.session.delete(obj)
        else:
            obj.ativo = False  # só se existir esse campo no modelo
        self.session.commit()
        return True
