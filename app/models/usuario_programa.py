# app/models/usuario_programa.py
from __future__ import annotations
from datetime import date
from typing import Optional

from sqlalchemy import UniqueConstraint, ForeignKey, String, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UsuarioPrograma(Base):
    """Association Object entre auth.usuarios e core.programas."""
    __tablename__ = "usuarios_programas"
    __table_args__ = (
        UniqueConstraint("usuario_id", "programa_id", name="uq_usuario_programa"),
        {"schema": "auth"},
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("auth.usuarios.id", ondelete="CASCADE"), index=True, nullable=False)
    programa_id: Mapped[int] = mapped_column(ForeignKey("core.programas.id", ondelete="CASCADE"), index=True, nullable=False)

    # Metadados do vínculo
    papel: Mapped[str] = mapped_column(String(30), default="Membro")    # Coordenador|Docente|Discente|Secretaria...
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    data_inicio: Mapped[Optional[date]] = mapped_column(Date)
    data_fim: Mapped[Optional[date]] = mapped_column(Date)

    # Relacionamentos: não exigimos back_populates no seu Usuario
    programa = relationship("Programa", back_populates="membros_assoc", lazy="joined")
    usuario = relationship("Usuario", lazy="joined")  # seu modelo `auth.Usuario` já existente
