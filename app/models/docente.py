# app/models/docente.py
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    Boolean,
    Date,
    Text,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Docente(Base):
    """
    ORM para academic.docentes.

    Representa os docentes vinculados a um Programa de Pós-Graduação.
    Contém informações acadêmicas, métricas de produção científica e vínculo institucional.
    """

    __tablename__ = "docentes"
    __table_args__ = (
        UniqueConstraint("usuario_id", "programa_id", name="uq_docente_usuario_programa"),
        CheckConstraint(
            "data_desvinculacao IS NULL OR data_desvinculacao >= data_vinculacao",
            name="ck_docente_datas",
        ),
        {"schema": "academic"},  # ✅ sempre por último
    )

    # Chave primária
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Relacionamentos
    usuario_id: Mapped[int] = mapped_column(ForeignKey("auth.usuarios.id"), nullable=False)
    programa_id: Mapped[int] = mapped_column(ForeignKey("core.programas.id"), nullable=False)
    linha_pesquisa_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("core.linhas_pesquisa.id"), nullable=True
    )

    # Dados específicos
    matricula: Mapped[Optional[str]] = mapped_column(String(50))
    categoria: Mapped[Optional[str]] = mapped_column(String(50))  # Titular, Associado, etc.
    regime_trabalho: Mapped[Optional[str]] = mapped_column(String(50))  # DE, 40h, 20h
    titulacao_maxima: Mapped[Optional[str]] = mapped_column(String(100))
    instituicao_titulacao: Mapped[Optional[str]] = mapped_column(String(255))
    ano_titulacao: Mapped[Optional[int]]
    pais_titulacao: Mapped[Optional[str]] = mapped_column(String(50))

    # Vínculo institucional
    tipo_vinculo: Mapped[str] = mapped_column(String(50), nullable=False)  # Permanente, Colaborador, etc.
    data_vinculacao: Mapped[date] = mapped_column(Date, nullable=False)
    data_desvinculacao: Mapped[Optional[date]]

    # Métricas acadêmicas
    h_index: Mapped[int] = mapped_column(Integer, default=0)
    total_publicacoes: Mapped[int] = mapped_column(Integer, default=0)
    total_citacoes: Mapped[int] = mapped_column(Integer, default=0)
    publicacoes_ultimos_5_anos: Mapped[int] = mapped_column(Integer, default=0)

    # Orientações
    orientacoes_mestrado_andamento: Mapped[int] = mapped_column(Integer, default=0)
    orientacoes_doutorado_andamento: Mapped[int] = mapped_column(Integer, default=0)
    orientacoes_mestrado_concluidas: Mapped[int] = mapped_column(Integer, default=0)
    orientacoes_doutorado_concluidas: Mapped[int] = mapped_column(Integer, default=0)
    coorientacoes: Mapped[int] = mapped_column(Integer, default=0)

    # Bolsas
    bolsista_produtividade: Mapped[bool] = mapped_column(Boolean, default=False)
    nivel_bolsa_produtividade: Mapped[Optional[str]] = mapped_column(String(20))
    vigencia_bolsa_inicio: Mapped[Optional[date]]
    vigencia_bolsa_fim: Mapped[Optional[date]]

    # Dados complementares
    areas_interesse: Mapped[Optional[str]] = mapped_column(Text)
    projetos_atuais: Mapped[Optional[str]] = mapped_column(Text)
    curriculo_resumo: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="Ativo")
    motivo_desligamento: Mapped[Optional[str]] = mapped_column(Text)

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    # Relações ORM
    usuario = relationship("Usuario", back_populates="docentes")
    programa = relationship("Programa", back_populates="docentes")
    # linha_pesquisa = relationship("LinhaPesquisa", back_populates="docentes") TODO: implementar linha de pesquisa futuramente
