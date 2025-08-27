from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# ---- BASE -----

class UsuarioBase(BaseModel):
    """
    Esquema base para um usuario.
    Base para todos os Schemas de Usuario
    Contém atributos comuns a todos os esquemas. CREATE, UPDATE, READ, LIST.
    """

    email: EmailStr
    nome_completo: Optional[str] = None
    role_id: int
    ativo: Optional[bool] = True

# ---- CREATE -----
class UsuarioCreate(UsuarioBase):
    """
    Esquema para criação de um usuario.
    Herda de UsuarioBase e adiciona o campo senha.
    """

    senha: str

# ---- UPDATE -----
# ----------------- UPDATE -----------------
class UsuarioUpdate(BaseModel):
    """
    Schema usado para atualização parcial de usuários.
    Todos os campos são opcionais para permitir patch.
    """
    email: Optional[EmailStr] = None
    nome_completo: Optional[str] = None
    role_id: Optional[int] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = None  # caso queira alterar senha

    model_config = ConfigDict(from_attributes=True)

# ----------------- OUTPUT -----------------
class UsuarioOut(UsuarioBase):
    """
    Schema usado nas respostas da API.
    Inclui o ID do usuário e oculta o campo de senha.
    """
    id: int

