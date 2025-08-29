from __future__ import annotations
from __future__ import annotations
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class RoleBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    nivel_acesso: int = 1
    permissoes: Dict[str, Any] = {}
    ativo: bool = True

    model_config = ConfigDict(from_attributes=True)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    nivel_acesso: Optional[int] = None
    permissoes: Optional[Dict[str, Any]] = None
    ativo: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class RoleOut(RoleBase):
    id: int

class RoleRead(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    nivel_acesso: int = 1
    permissoes: Dict[str, Any] = {}
    ativo: bool = True

    model_config = ConfigDict(from_attributes=True)
