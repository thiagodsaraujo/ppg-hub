from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Instituicao(Base):
    """Modelo ORM para a tabela core.instituicoes."""

    __tablename__ = "instituicoes"
    __table_args__ = (
        UniqueConstraint("codigo", name="uq_instituicao_codigo"),
        UniqueConstraint("sigla", name="uq_instituicao_sigla"),
        {"schema": "core"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    nome_completo: Mapped[str] = mapped_column(String(500), nullable=False)
    nome_abreviado: Mapped[str] = mapped_column(String(50), nullable=False)
    sigla: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(20))
    natureza_juridica: Mapped[str | None] = mapped_column(String(100))

    endereco: Mapped[dict | None] = mapped_column(JSON, default={})
    contatos: Mapped[dict | None] = mapped_column(JSON, default={})
    redes_sociais: Mapped[dict | None] = mapped_column(JSON, default={})

    logo_url: Mapped[str | None] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(255))
    fundacao: Mapped[str | None] = mapped_column(String(50))
    openalex_institution_id: Mapped[str | None] = mapped_column(String(50))
    ror_id: Mapped[str | None] = mapped_column(String(50))

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    configuracoes: Mapped[dict | None] = mapped_column(JSON, default={})

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
