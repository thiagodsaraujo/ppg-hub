from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict


# ---- BASE -----
class UsuarioBase(BaseModel):
    """
    Esquema base para um usuário.
    Base para todos os Schemas de Usuário
    Contém atributos comuns a CREATE, UPDATE, READ e LIST.
    """

    email: EmailStr
    nome_completo: Optional[str] = None
    role_id: int
    ativo: Optional[bool] = True

    model_config = ConfigDict(from_attributes=True)


# ---- CREATE -----
class UsuarioCreate(UsuarioBase):
    """
    Esquema para criação de um usuário.
    Herda de UsuarioBase e adiciona o campo senha.
    """
    senha: str


# ---- UPDATE -----
class UsuarioUpdate(BaseModel):
    """
    Schema usado para atualização parcial de usuários (PATCH).
    Todos os campos são opcionais para permitir atualização seletiva.
    """
    email: Optional[EmailStr] = None
    nome_completo: Optional[str] = None
    role_id: Optional[int] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = None  # caso queira alterar senha

    model_config = ConfigDict(from_attributes=True)


# ---- READ (OUTPUT) -----
class UsuarioRead(UsuarioBase):
    """
    Schema usado para respostas da API (GET).
    Inclui o ID do usuário e oculta o campo de senha.
    """
    id: int


# ---- LIST (PAGINADO) -----
class UsuarioList(BaseModel):
    """
    Schema para listagem paginada de usuários.
    Retorna a lista de usuários e o total de registros.
    """
    items: List[UsuarioRead]
    total: int
