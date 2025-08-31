from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import select, func

from app.models.docente import Docente
from app.schemas.docente import DocenteCreate, DocenteUpdate


class DocenteRepository:
    """Repositório para operações de banco de dados relacionadas a Docente."""

    def __init__(self, session):
        self.session = session

        # --------------------------------------------------------
        # CREATE
        # --------------------------------------------------------

    def create(self, data: DocenteCreate) -> Docente:
        """Cria um novo docente no banco de dados."""
        # Cria uma nova instância de Docente usando os dados fornecidos
        new_docente = Docente(**data.model_dump())
        # Adiciona o novo docente à sessão do banco de dados
        self.session.add(new_docente)
        # Salva as alterações no banco de dados
        self.session.commit()
        # Atualiza o objeto com dados do banco (ex: campos gerados)
        self.session.refresh(new_docente)
        # Retorna o docente recém-criado
        return new_docente

    # ---------------------------
    # GET by ID
    # ---------------------------
    def get(self, docente_id: int) -> Optional[Docente]:
        stmt = select(Docente).where(Docente.id == docente_id)
        return self.session.scalar(stmt)

    # ---------------------------
    # LIST (com paginação)
    # ---------------------------
    def list(self, skip: int = 0, limit: int = 10) -> Tuple[List[Docente], int]:
        """Lista docentes com paginação (items, total)."""
        stmt = select(Docente).offset(skip).limit(limit)
        items = list(self.session.scalars(stmt).all())
        total = self.session.scalar(select(func.count()).select_from(Docente))
        return items, total

    # ---------------------------
    # LIST ALL (sem paginação)
    # ---------------------------
    def list_all(self) -> List[Docente]:
        """Lista todos os docentes (sem paginação)."""
        stmt = select(Docente)
        return list(self.session.scalars(stmt).all())

    # ---------------------------
    # UPDATE
    # ---------------------------
    def update(self, docente: Docente, data: DocenteUpdate) -> Docente:
        """Atualiza dados de um docente existente."""
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(docente, field, value)
        self.session.add(docente)
        self.session.commit()
        self.session.refresh(docente)
        return docente

        # ---------------------------
        # DELETE
        # ---------------------------

    def delete(self, docente: Docente) -> None:
        """Remove um docente do banco."""
        self.session.delete(docente)
        self.session.commit()

