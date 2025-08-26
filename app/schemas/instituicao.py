from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


# ----- Base -----
class InstituicaoBase(BaseModel):
    codigo: str = Field(..., json_schema_extra={"example": "UEPB"})
    nome_completo: str
    nome_abreviado: str
    sigla: str
    tipo: str
    cnpj: Optional[str] = None
    natureza_juridica: Optional[str] = None
    endereco: Optional[dict] = Field(default_factory=dict)
    contatos: Optional[dict] = Field(default_factory=dict)
    redes_sociais: Optional[dict] = Field(default_factory=dict)
    logo_url: Optional[str] = None
    website: Optional[str] = None
    fundacao: Optional[str] = None
    openalex_institution_id: Optional[str] = None
    ror_id: Optional[str] = None
    ativo: bool = True
    configuracoes: Optional[dict] = Field(default_factory=dict)


# ----- Create -----
class InstituicaoCreate(InstituicaoBase):
    pass


# ----- Update -----
class InstituicaoUpdate(BaseModel):
    nome_completo: Optional[str] = None
    nome_abreviado: Optional[str] = None
    sigla: Optional[str] = None
    tipo: Optional[str] = None
    cnpj: Optional[str] = None
    natureza_juridica: Optional[str] = None
    endereco: Optional[dict] = None
    contatos: Optional[dict] = None
    redes_sociais: Optional[dict] = None
    logo_url: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None
    fundacao: Optional[str] = None
    openalex_institution_id: Optional[str] = None
    ror_id: Optional[str] = None
    ativo: Optional[bool] = None
    configuracoes: Optional[dict] = None


# ----- Read -----
class InstituicaoRead(InstituicaoBase):
    id: int

    class Config:
        from_attributes = True


# ----- Paginated -----
class InstituicaoList(BaseModel):
    items: list[InstituicaoRead]
    total: int
