# app/schemas/docente.py
from __future__ import annotations

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# --------------------------------------------------------
# Base comum (campos compartilhados entre create/update/read)
# --------------------------------------------------------
class DocenteBase(BaseModel):
    """Campos básicos de Docente (compartilhados entre create/update/read)."""

    matricula: Optional[str] = None
    categoria: Optional[str] = None               # Titular, Associado, Adjunto...
    regime_trabalho: Optional[str] = None         # DE, 40h, 20h
    titulacao_maxima: Optional[str] = None
    instituicao_titulacao: Optional[str] = None
    ano_titulacao: Optional[int] = None
    pais_titulacao: Optional[str] = None

    tipo_vinculo: str                             # Permanente, Colaborador, Visitante
    data_vinculacao: date                         # Início do vínculo
    data_desvinculacao: Optional[date] = None     # Pode ser nula

    h_index: int = 0
    total_publicacoes: int = 0
    total_citacoes: int = 0
    publicacoes_ultimos_5_anos: int = 0

    orientacoes_mestrado_andamento: int = 0
    orientacoes_doutorado_andamento: int = 0
    orientacoes_mestrado_concluidas: int = 0
    orientacoes_doutorado_concluidas: int = 0
    coorientacoes: int = 0

    bolsista_produtividade: bool = False
    nivel_bolsa_produtividade: Optional[str] = None
    vigencia_bolsa_inicio: Optional[date] = None
    vigencia_bolsa_fim: Optional[date] = None

    areas_interesse: Optional[str] = None
    projetos_atuais: Optional[str] = None
    curriculo_resumo: Optional[str] = None

    status: str = "Ativo"                         # Ativo, Afastado, Aposentado...
    motivo_desligamento: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------
# Schema de criação (requere IDs obrigatórios)
# --------------------------------------------------------
class DocenteCreate(DocenteBase):
    """Schema usado na criação de Docente."""

    usuario_id: int   # FK → auth.usuarios
    programa_id: int  # FK → core.programas
    # linha_pesquisa_id deixamos de fora pq você ainda não implementou


# --------------------------------------------------------
# Schema de atualização (todos os campos opcionais)
# --------------------------------------------------------
class DocenteUpdate(BaseModel):
    """Schema usado na atualização parcial de Docente."""

    matricula: Optional[str] = None
    categoria: Optional[str] = None
    regime_trabalho: Optional[str] = None
    titulacao_maxima: Optional[str] = None
    instituicao_titulacao: Optional[str] = None
    ano_titulacao: Optional[int] = None
    pais_titulacao: Optional[str] = None

    tipo_vinculo: Optional[str] = None
    data_vinculacao: Optional[date] = None
    data_desvinculacao: Optional[date] = None

    h_index: Optional[int] = None
    total_publicacoes: Optional[int] = None
    total_citacoes: Optional[int] = None
    publicacoes_ultimos_5_anos: Optional[int] = None

    orientacoes_mestrado_andamento: Optional[int] = None
    orientacoes_doutorado_andamento: Optional[int] = None
    orientacoes_mestrado_concluidas: Optional[int] = None
    orientacoes_doutorado_concluidas: Optional[int] = None
    coorientacoes: Optional[int] = None

    bolsista_produtividade: Optional[bool] = None
    nivel_bolsa_produtividade: Optional[str] = None
    vigencia_bolsa_inicio: Optional[date] = None
    vigencia_bolsa_fim: Optional[date] = None

    areas_interesse: Optional[str] = None
    projetos_atuais: Optional[str] = None
    curriculo_resumo: Optional[str] = None

    status: Optional[str] = None
    motivo_desligamento: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------
# Schema de saída (quando retornamos Docente ao cliente)
# --------------------------------------------------------
class DocenteRead(DocenteBase):
    """Schema usado na resposta da API para Docente."""

    id: int
    usuario_id: int
    programa_id: int
    created_at: datetime
    updated_at: datetime


# --------------------------------------------------------
# Lista paginada de docentes
# --------------------------------------------------------
class DocenteList(BaseModel):
    """Retorno paginado de docentes."""

    items: List[DocenteRead]
    total: int
