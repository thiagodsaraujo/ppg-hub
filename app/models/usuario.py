from typing import Optional

from sqlalchemy import Integer, String, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.role import Role


class Usuario(Base):
    """Modelo de Usuario."""

    __tablename__ = 'usuarios'
    __table_args__ = {'schema': 'auth'}

    # PK
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    # Identificação
    email: Mapped[String] = mapped_column(String(255), unique=True, index=True, nullable=False)
    senha_hash: Mapped[String] = mapped_column(String(255), nullable=False) # Armazena o hash da senha
    nome_completo: Mapped[Optional[str]] = mapped_column(String(255), nullable=False)

    # Controle de Acesso
    role_id: Mapped[int] = mapped_column(ForeignKey('auth.roles.id'), nullable=False)
    role: Mapped[Role] = relationship("Role", backref="usuarios")

    # Status
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    criado_em: Mapped[Optional[str]] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    atualizado_em: Mapped[Optional[str]] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )