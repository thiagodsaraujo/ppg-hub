from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ----------------- BASE -----------------
class ProgramaBase(BaseModel):
    """
    Esquema base de Programa.
    Campos comuns para Create, Update, Read e List.
    """

    instituicao_id: int
    codigo_capes: Optional[str] = None
    nome: str
    sigla: str
    area_concentracao: Optional[str] = None
    nivel: str  # Mestrado, Doutorado, Mestrado/Doutorado
    modalidade: Optional[str] = "Presencial"
    status: Optional[str] = "Ativo"

    model_config = ConfigDict(from_attributes=True)


# ----------------- CREATE -----------------
class ProgramaCreate(ProgramaBase):
    """
    Esquema usado para criação de Programa.
    Herda de ProgramaBase.
    """
    pass


# ----------------- UPDATE -----------------
class ProgramaUpdate(BaseModel):
    """
    Esquema usado para atualização parcial de Programa (PATCH/PUT).
    Todos os campos são opcionais para permitir atualização seletiva.
    """
    instituicao_id: Optional[int] = None
    codigo_capes: Optional[str] = None
    nome: Optional[str] = None
    sigla: Optional[str] = None
    area_concentracao: Optional[str] = None
    nivel: Optional[str] = None
    modalidade: Optional[str] = None
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------- READ -----------------
class ProgramaRead(ProgramaBase):
    """
    Esquema usado para respostas da API (GET).
    Inclui o ID do programa.
    """
    id: int


# ----------------- LIST (PAGINADO) -----------------
class ProgramaList(BaseModel):
    """
    Esquema para listagem paginada de Programas.
    Retorna a lista de Programas e o total de registros.
    """
    items: List[ProgramaRead]
    total: int
