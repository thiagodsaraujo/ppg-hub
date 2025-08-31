# app/models/programa.py
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    String, Integer, Date, DateTime, ForeignKey,
    UniqueConstraint, CheckConstraint, Index, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict  # <- rastrear mutações em JSONB

from app.db.base import Base


class Programa(Base):
    """ORM para core.programas.

    Regras:
      - (instituicao_id, sigla) é único por schema.
      - conceito_capes ∈ [1,7] quando não nulo.
      - JSONB 'configuracoes' é mutável (mudanças in-place são rastreadas).
    """
    __tablename__ = "programas"
    __table_args__ = (
        UniqueConstraint("instituicao_id", "sigla", name="uq_programa_instituicao_sigla"),
        CheckConstraint(
            "conceito_capes IS NULL OR (conceito_capes BETWEEN 1 AND 7)",
            name="ck_programa_conceito_capes_1_7",
        ),
        # Índices adicionais úteis (além dos implícitos por PK/UK)
        Index("ix_programas_nome", "nome"),
        {"schema": "core"},
    )

    # Identificação / vínculo institucional
    id: Mapped[int] = mapped_column(primary_key=True)  # PK já é indexada pelo Postgres
    instituicao_id: Mapped[int] = mapped_column(
        ForeignKey("core.instituicoes.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        doc="Instituição mantenedora deste Programa.",
    )

    # Dentro da classe Programa
    docentes = relationship("Docente", back_populates="programa")

    # Identificação acadêmica
    codigo_capes: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,  # Postgres permite múltiplos NULLs (ok)
        nullable=True,
        doc="Código CAPES do Programa (quando existir).",
    )
    nome: Mapped[str] = mapped_column(
        String(255), nullable=False, doc="Nome oficial do Programa."
    )
    sigla: Mapped[str] = mapped_column(
        String(20), nullable=False, doc="Sigla do Programa (única por instituição)."
    )
    area_concentracao: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    # Natureza do curso
    nivel: Mapped[str] = mapped_column(
        String(50), nullable=False, doc="Ex.: Mestrado, Doutorado."
    )
    modalidade: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="Presencial", doc="Ex.: Presencial, EAD, Híbrido."
    )

    # Datas / avaliação CAPES
    inicio_funcionamento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    conceito_capes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    data_ultima_avaliacao: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    trienio_avaliacao: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Configuração / governança
    configuracoes: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSONB),  # <- essencial para tracking
        nullable=False,
        server_default="{}",
        doc="Configurações dinâmicas do Programa (JSONB).",
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="Ativo"
    )

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Associação (membros do programa)
    usuarios_roles = relationship(
        "UsuarioProgramaRole",
        back_populates="programa",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # (Opcional) Ajuda no debug
    def __repr__(self) -> str:
        return f"<Programa id={self.id} inst={self.instituicao_id} sigla={self.sigla!r}>"
