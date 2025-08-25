from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON
from app.db.base import Base

class Instituicao(Base):
    """Representa uma instituição (ex.: universidade, centro, hospital).

    Decisões de modelagem:
        - `codigo` e `sigla` são únicos por negócio (UniqueConstraint).
        - Alguns campos externos (OpenAlex/ROR) são opcionais para integrações.
        - Blocos JSON (endereco, contatos, redes_sociais, configuracoes) permitem flexibilidade
          sem precisar criar várias tabelas auxiliares neste primeiro momento.
        - `ativa` controla soft-estado operacional; não removemos fisicamente por padrão.
        - `created_at`/`updated_at` dão rastreabilidade temporal a qualquer mudança.
    """

    __tablename__ = "instituicoes"
    __table_args__ = (
        # Regras de unicidade de negócio:
        UniqueConstraint("codigo", name="uq_instituicao_codigo"),
        UniqueConstraint("sigla", name="uq_instituicao_sigla"),
    )

    # PK inteira com índice para buscas rápidas por id
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Identificador interno curto para integração/negócio (search rápido -> index=True)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # Nome jurídico/social completo (até 500 chars para nomes longos)
    nome_completo: Mapped[str] = mapped_column(String(500), nullable=False)

    # Um nome curto para telas/documentos onde o completo não cabe
    nome_abreviado: Mapped[str] = mapped_column(String(50), nullable=False)

    # Sigla institucional (ex.: UEPB). Única e indexada, pois é muito consultada
    sigla: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Classificação da instituição (ex.: "Universidade", "Centro", "Hospital")
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)

    # CNPJ opcional e único. Guardamos formatado ou só dígitos (decidir política depois)
    cnpj: Mapped[str | None] = mapped_column(String(18), nullable=True, unique=True)

    # Natureza jurídica (ex.: "Autarquia", "Fundação", "Empresa Pública")
    natureza_juridica: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Blocos sem esquema rígido — úteis para projeto em evolução:
    # Trade-off: flexibilidade vs. menor validação no banco.
    endereco: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    contatos: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    redes_sociais: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Metadados públicos
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Fundação pode ser data exata (ou só ano; se precisar só ano, discutir modelagem)
    fundacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)

    # IDs externos para integrações acadêmicas/científicas
    openalex_institution_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ror_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Soft state (ativa/desativada) — server_default mantém coerência no lado do DB
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    # Configurações variadas (feature flags, preferências de relatórios, etc.)
    configuracoes: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict, server_default="{}")

    # Auditoria (timestamps automáticos no servidor)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now()
    )
