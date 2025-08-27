# app/schemas/programa.py
from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ProgramaCreate(BaseModel):
    """Entrada para criação de Programa."""
    instituicao_id: int
    nome: str
    sigla: str = Field(..., max_length=20)
    nivel: str
    modalidade: str = "Presencial"
    codigo_capes: Optional[str] = None
    area_concentracao: Optional[str] = None
    inicio_funcionamento: Optional[date] = None
    conceito_capes: Optional[int] = None
    data_ultima_avaliacao: Optional[date] = None
    trienio_avaliacao: Optional[str] = None
    configuracoes: dict = Field(default_factory=dict)
    status: str = "Ativo"

class ProgramaOut(BaseModel):
    """Saída de Programa."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    instituicao_id: int
    nome: str
    sigla: str
    nivel: str
    modalidade: str
    codigo_capes: Optional[str]
    area_concentracao: Optional[str]
    inicio_funcionamento: Optional[date]
    conceito_capes: Optional[int]
    data_ultima_avaliacao: Optional[date]
    trienio_avaliacao: Optional[str]
    configuracoes: dict
    status: str
