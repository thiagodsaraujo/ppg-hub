from __future__ import annotations
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ----------------- BASE -----------------
class UsuarioProgramaRoleBase(BaseModel):
    """
    Schema base para vínculo usuário-programa-role.
    Campos comuns usados em Create, Update e Read.
    """

    usuario_id: int
    programa_id: int
    role_id: int
    data_vinculacao: Optional[date] = None
    data_desvinculacao: Optional[date] = None
    status: Optional[str] = "Ativo"   # Ativo, Suspenso, Desligado
    observacoes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------- CREATE -----------------
class UsuarioProgramaRoleCreate(UsuarioProgramaRoleBase):
    """
    Schema para criação de vínculo usuário-programa.
    Todos os campos obrigatórios, exceto datas/observações opcionais.
    """
    pass


# ----------------- UPDATE -----------------
class UsuarioProgramaRoleUpdate(BaseModel):
    """
    Schema para atualização parcial do vínculo (PATCH/PUT).
    Todos os campos opcionais.
    """

    usuario_id: Optional[int] = None
    programa_id: Optional[int] = None
    role_id: Optional[int] = None
    data_vinculacao: Optional[date] = None
    data_desvinculacao: Optional[date] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------- READ -----------------
class UsuarioProgramaRoleRead(UsuarioProgramaRoleBase):
    """
    Schema de resposta (GET).
    Inclui ID e metadados.
    """

    id: int
    created_at: datetime
    created_by: Optional[int] = None


# ----------------- LIST (PAGINADO) -----------------
class UsuarioProgramaRoleList(BaseModel):
    """
    Schema para listagem paginada de vínculos usuário-programa.
    """
    items: List[UsuarioProgramaRoleRead]
    total: int
