# app/schemas/usuario_programa.py
from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

class VincularUsuarioProgramaIn(BaseModel):
    """Entrada: vínculo de usuário a programa."""
    usuario_id: int
    papel: str = "Membro"
    ativo: bool = True
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None

class UsuarioProgramaOut(BaseModel):
    """Saída do vínculo (association object)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: int
    programa_id: int
    papel: str
    ativo: bool
    data_inicio: Optional[date]
    data_fim: Optional[date]
