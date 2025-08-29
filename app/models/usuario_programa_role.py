from __future__ import annotations
from datetime import datetime, date
from sqlalchemy import Integer, String, Date, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UsuarioProgramaRole(Base):
    """
    ORM para a tabela auth.usuario_programa_roles.
    Representa o vínculo de um usuário com um programa,
    incluindo o papel (role), status e histórico de datas.
    """

    __tablename__ = "usuario_programa_roles"
    __table_args__ = (
        UniqueConstraint("usuario_id", "programa_id", "role_id", name="uq_usuario_programa_role"),
        CheckConstraint(
            "data_desvinculacao IS NULL OR data_desvinculacao >= data_vinculacao",
            name="ck_datas_vinculo"
        ),
        {"schema": "auth"},
    )

    # ----------------- CAMPOS -----------------
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("auth.usuarios.id", ondelete="CASCADE"), nullable=False
    )
    programa_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("core.programas.id", ondelete="CASCADE"), nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("auth.roles.id", ondelete="CASCADE"), nullable=False
    )

    data_vinculacao: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    data_desvinculacao: Mapped[date | None] = mapped_column(Date, nullable=True)

    status: Mapped[str] = mapped_column(String(50), default="Ativo", nullable=False)  # Ativo, Suspenso, Desligado
    observacoes: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("auth.usuarios.id"), nullable=True
    )

    # ----------------- RELACIONAMENTOS -----------------
    usuario = relationship("Usuario", back_populates="programas_roles", foreign_keys=[usuario_id])
    programa = relationship("Programa", back_populates="usuarios_roles", foreign_keys=[programa_id])
    role = relationship("Role", back_populates="usuarios_roles", foreign_keys=[role_id])
