# app/models/programa.py
from __future__ import annotations
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    String, Integer, Date, DateTime, ForeignKey,
    UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class Programa(Base):
    """ORM para core.programas (alinhado ao seu SQL)."""
    __tablename__ = "programas"
    __table_args__ = (
        UniqueConstraint("instituicao_id", "sigla", name="uq_programa_instituicao_sigla"),
        CheckConstraint(
            "conceito_capes IS NULL OR (conceito_capes BETWEEN 1 AND 7)",
            name="ck_programa_conceito_capes_1_7",
        ),
        {"schema": "core"},
    )

    # Identificação / vínculo institucional
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    instituicao_id: Mapped[int] = mapped_column(ForeignKey("core.instituicoes.id", ondelete="RESTRICT"), index=True)

    # Identificação acadêmica
    codigo_capes: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    nome: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    sigla: Mapped[str] = mapped_column(String(20), nullable=False)
    area_concentracao: Mapped[Optional[str]] = mapped_column(String(255))

    # Natureza do curso
    nivel: Mapped[str] = mapped_column(String(50), nullable=False)          # Mestrado, Doutorado...
    modalidade: Mapped[str] = mapped_column(String(50), default="Presencial")

    # Datas / avaliação CAPES
    inicio_funcionamento: Mapped[Optional[date]] = mapped_column(Date)
    conceito_capes: Mapped[Optional[int]] = mapped_column(Integer)
    data_ultima_avaliacao: Mapped[Optional[date]] = mapped_column(Date)
    trienio_avaliacao: Mapped[Optional[str]] = mapped_column(String(20))

    # Configuração / governança
    configuracoes: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Ativo", nullable=False)

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Associação (membros do programa) — não força back_populates no seu Usuario
    membros_assoc = relationship(
        "UsuarioPrograma",
        back_populates="programa",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
