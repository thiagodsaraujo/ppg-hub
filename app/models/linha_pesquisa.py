# app/models/linha_pesquisa.py
from __future__ import annotations
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class LinhaPesquisa(Base):
    """ORM para core.linhas_pesquisa."""
    __tablename__ = "linhas_pesquisa"
    __table_args__ = {"schema": "core"}  # ✅ importante

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    programa_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("core.programas.id", ondelete="CASCADE"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    palavras_chave: Mapped[str | None] = mapped_column(Text)

    # opcional: backref para docentes se você tiver relationship lá
