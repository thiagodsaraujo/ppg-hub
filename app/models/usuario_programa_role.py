# app/models/usuario_programa_role.py
from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import (
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UsuarioProgramaRole(Base):
    """
    ORM para a tabela auth.usuario_programa_roles.
    Representa o vínculo de um usuário com um programa e seu papel (role),
    incluindo status e histórico de datas.
    """

    __tablename__ = "usuarios_programas"
    __table_args__ = (
        UniqueConstraint(
            "usuario_id", "programa_id", "role_id",
            name="uq_usuario_programa_role_new",
        ),
        CheckConstraint(
            "data_desvinculacao IS NULL OR data_desvinculacao >= data_vinculacao",
            name="ck_datas_vinculo",
        ),
        {"schema": "auth"},
    )

    # ----------------- COLUNAS -----------------
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)

    # FKs principais
    usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("auth.usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    programa_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("core.programas.id", ondelete="CASCADE"),
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("auth.roles.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Datas de vínculo
    data_vinculacao: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    data_desvinculacao: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Status e observações
    status: Mapped[str] = mapped_column(String(50), default="Ativo", nullable=False)  # Ativo | Suspenso | Desligado
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("auth.usuarios.id"),
        nullable=True,
    )

    # ----------------- RELACIONAMENTOS -----------------
    # IMPORTANTE: como há MAIS DE UMA FK para auth.usuarios neste modelo (usuario_id, created_by),
    # precisamos FIXAR explicitamente foreign_keys no relationship principal para evitar ambiguidade.
    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="programas_roles",
        foreign_keys=lambda: [UsuarioProgramaRole.usuario_id],
    )

    programa: Mapped["Programa"] = relationship(
        "Programa",
        back_populates="usuarios_roles",
        foreign_keys=lambda: [UsuarioProgramaRole.programa_id],
    )

    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="usuarios_roles",
        foreign_keys=lambda: [UsuarioProgramaRole.role_id],
    )

    # Relacionamento opcional apenas para navegação do autor de criação (sem back_populates para não exigir atributo no Usuario)
    created_by_usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        foreign_keys=lambda: [UsuarioProgramaRole.created_by],
        viewonly=True,
    )

    # ----------------- DUNDERS -----------------
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"UsuarioProgramaRole(id={self.id}, usuario_id={self.usuario_id}, "
            f"programa_id={self.programa_id}, role_id={self.role_id}, status='{self.status}')"
        )
