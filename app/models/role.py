from __future__ import annotations
from typing import Optional, Dict, Any
from sqlalchemy import Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base

class Role(Base):
    """Modelo ORM para papéis (RBAC)."""
    __tablename__ = "roles"
    __table_args__ = {"schema": "auth"}

    # PK
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Campos em PT-BR, alinhados aos testes e ao repositório
    nome: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    nivel_acesso: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    permissoes: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default="{}"  # no Postgres vira '{}'::jsonb
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps (timezone-aware no Postgres)
    criado_em: Mapped[Optional[Any]] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    atualizado_em: Mapped[Optional[Any]] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )
