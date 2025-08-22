"""
Schemas Pydantic para Instituição.

Define os modelos de entrada e saída da API usando Pydantic v2.
Separa claramente dados de entrada (request) dos dados de saída (response).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict, validator
from pydantic import HttpUrl


# === SCHEMAS BASE ===
class InstituicaoBase(BaseModel):
    """
    Schema base com campos comuns para Instituição.

    Contém campos que são compartilhados entre create/update/read.
    Outros schemas herdam deste para evitar duplicação.
    """

    codigo: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="Código único da instituição (ex: UEPB, UFCG)",
        example="UEPB"
    )

    nome_completo: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Nome oficial completo da instituição",
        example="Universidade Estadual da Paraíba"
    )

    nome_abreviado: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Nome abreviado para exibição",
        example="UEPB"
    )

    sigla: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="Sigla oficial da instituição",
        example="UEPB"
    )

    tipo: str = Field(
        ...,
        description="Tipo da instituição",
        example="Estadual"
    )

    cnpj: Optional[str] = Field(
        None,
        min_length=14,
        max_length=18,
        description="CNPJ da instituição (com ou sem formatação)",
        example="12.345.678/0001-90"
    )

    natureza_juridica: Optional[str] = Field(
        None,
        max_length=100,
        description="Natureza jurídica detalhada",
        example="Autarquia Estadual"
    )

    endereco: Optional[Dict[str, Any]] = Field(
        None,
        description="Dados de endereço em formato JSON",
        example={
            "logradouro": "Rua Baraúnas, 351",
            "bairro": "Universitário",
            "cidade": "Campina Grande",
            "uf": "PB",
            "cep": "58429-500",
            "complemento": "Campus I"
        }
    )

    contatos: Optional[Dict[str, Any]] = Field(
        None,
        description="Telefones e emails em formato JSON",
        example={
            "email_principal": "contato@uepb.edu.br",
            "telefone_principal": "(83) 3315-3300",
            "emails": ["contato@uepb.edu.br", "reitoria@uepb.edu.br"],
            "telefones": ["(83) 3315-3300", "(83) 3315-3301"]
        }
    )

    redes_sociais: Optional[Dict[str, Any]] = Field(
        None,
        description="URLs das redes sociais",
        example={
            "facebook": "https://facebook.com/uepb.oficial",
            "instagram": "https://instagram.com/uepb.oficial",
            "twitter": "https://twitter.com/uepb_oficial",
            "linkedin": "https://linkedin.com/school/uepb"
        }
    )

    logo_url: Optional[HttpUrl] = Field(
        None,
        description="URL do logotipo da instituição",
        example="https://uepb.edu.br/assets/logo.png"
    )

    website: Optional[HttpUrl] = Field(
        None,
        description="Site oficial da instituição",
        example="https://uepb.edu.br"
    )

    fundacao: Optional[datetime] = Field(
        None,
        description="Data de fundação da instituição",
        example="1987-04-05T00:00:00"
    )

    openalex_institution_id: Optional[str] = Field(
        None,
        description="ID da instituição na base OpenAlex",
        example="I123456789"
    )

    ror_id: Optional[str] = Field(
        None,
        description="Research Organization Registry ID",
        example="https://ror.org/01234567"
    )

    ativo: bool = Field(
        True,
        description="Se a instituição está ativa no sistema"
    )

    configuracoes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configurações específicas da instituição",
        example={
            "cor_tema": "#0066cc",
            "timezone": "America/Sao_Paulo",
            "idioma_padrao": "pt-BR"
        }
    )


# === SCHEMA PARA CRIAÇÃO ===
class InstituicaoCreate(InstituicaoBase):
    """
    Schema para criação de instituição.

    Herda todos os campos de InstituicaoBase.
    Todos os campos obrigatórios devem ser fornecidos.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "codigo": "UEPB",
                "nome_completo": "Universidade Estadual da Paraíba",
                "nome_abreviado": "UEPB",
                "sigla": "UEPB",
                "tipo": "Estadual",
                "cnpj": "12.345.678/0001-90",
                "natureza_juridica": "Autarquia Estadual",
                "endereco": {
                    "logradouro": "Rua Baraúnas, 351",
                    "bairro": "Universitário",
                    "cidade": "Campina Grande",
                    "uf": "PB",
                    "cep": "58429-500"
                },
                "contatos": {
                    "email_principal": "contato@uepb.edu.br",
                    "telefone_principal": "(83) 3315-3300"
                },
                "website": "https://uepb.edu.br",
                "fundacao": "1987-04-05T00:00:00",
                "ativo": True
            }
        }
    )

    @validator("tipo")
    def validar_tipo(cls, v: str) -> str:
        """
        Valida se o tipo da instituição é válido.

        Args:
            v: Valor do tipo

        Returns:
            str: Tipo validado

        Raises:
            ValueError: Se tipo inválido
        """
        tipos_validos = ["Federal", "Estadual", "Municipal", "Privada"]
        if v not in tipos_validos:
            raise ValueError(f"Tipo deve ser um de: {', '.join(tipos_validos)}")
        return v

    @validator("cnpj")
    def validar_cnpj_formato(cls, v: Optional[str]) -> Optional[str]:
        """
        Valida formato básico do CNPJ.

        Args:
            v: CNPJ fornecido

        Returns:
            str: CNPJ formatado ou None

        Raises:
            ValueError: Se formato inválido
        """
        if v is None:
            return v

        # Remove formatação
        cnpj_limpo = v.replace(".", "").replace("/", "").replace("-", "")

        # Valida se tem 14 dígitos
        if len(cnpj_limpo) != 14 or not cnpj_limpo.isdigit():
            raise ValueError("CNPJ deve ter 14 dígitos numéricos")

        # Retorna formatado
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"

    @validator("codigo")
    def validar_codigo_formato(cls, v: str) -> str:
        """
        Valida formato do código da instituição.

        Args:
            v: Código fornecido

        Returns:
            str: Código validado em maiúsculo
        """
        # Converte para maiúsculo e remove espaços
        codigo_limpo = v.strip().upper()

        # Valida caracteres alfanuméricos
        if not codigo_limpo.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Código deve conter apenas letras, números, _ ou -")

        return codigo_limpo


# === SCHEMA PARA ATUALIZAÇÃO ===
class InstituicaoUpdate(BaseModel):
    """
    Schema para atualização de instituição.

    Todos os campos são opcionais para permitir atualização parcial.
    Apenas campos fornecidos serão atualizados.
    """

    codigo: Optional[str] = Field(
        None,
        min_length=2,
        max_length=20,
        description="Código único da instituição"
    )

    nome_completo: Optional[str] = Field(
        None,
        min_length=5,
        max_length=500,
        description="Nome oficial completo"
    )

    nome_abreviado: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        description="Nome abreviado"
    )

    sigla: Optional[str] = Field(
        None,
        min_length=2,
        max_length=10,
        description="Sigla oficial"
    )

    tipo: Optional[str] = Field(
        None,
        description="Tipo da instituição"
    )

    cnpj: Optional[str] = Field(
        None,
        description="CNPJ da instituição"
    )

    natureza_juridica: Optional[str] = Field(
        None,
        max_length=100,
        description="Natureza jurídica"
    )

    endereco: Optional[Dict[str, Any]] = Field(
        None,
        description="Dados de endereço"
    )

    contatos: Optional[Dict[str, Any]] = Field(
        None,
        description="Contatos"
    )

    redes_sociais: Optional[Dict[str, Any]] = Field(
        None,
        description="Redes sociais"
    )

    logo_url: Optional[HttpUrl] = Field(
        None,
        description="URL do logotipo"
    )

    website: Optional[HttpUrl] = Field(
        None,
        description="Site oficial"
    )

    fundacao: Optional[datetime] = Field(
        None,
        description="Data de fundação"
    )

    openalex_institution_id: Optional[str] = Field(
        None,
        description="ID OpenAlex"
    )

    ror_id: Optional[str] = Field(
        None,
        description="ROR ID"
    )

    ativo: Optional[bool] = Field(
        None,
        description="Status ativo"
    )

    configuracoes: Optional[Dict[str, Any]] = Field(
        None,
        description="Configurações específicas"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome_abreviado": "UEPB - Campus II",
                "contatos": {
                    "telefone_principal": "(83) 3315-3400"
                },
                "configuracoes": {
                    "cor_tema": "#ff6600"
                }
            }
        }
    )

    # Aplica os mesmos validators do Create quando campos estão presentes
    _validar_tipo = validator("tipo", allow_reuse=True)(InstituicaoCreate.validar_tipo)
    _validar_cnpj = validator("cnpj", allow_reuse=True)(InstituicaoCreate.validar_cnpj_formato)
    _validar_codigo = validator("codigo", allow_reuse=True)(InstituicaoCreate.validar_codigo_formato)


# === SCHEMA PARA RESPOSTA ===
class InstituicaoRead(InstituicaoBase):
    """
    Schema para resposta da API com dados da instituição.

    Inclui todos os campos de InstituicaoBase plus campos automáticos
    como ID, timestamps e campos calculados.
    """

    id: int = Field(
        ...,
        description="ID único da instituição"
    )

    created_at: datetime = Field(
        ...,
        description="Data de criação do registro"
    )

    updated_at: datetime = Field(
        ...,
        description="Data da última atualização"
    )

    # Campos calculados (computed properties)
    endereco_completo: str = Field(
        "",
        description="Endereço formatado completo"
    )

    contato_principal: str = Field(
        "",
        description="Email ou telefone principal"
    )

    model_config = ConfigDict(
        from_attributes=True,  # Permite conversão de modelos SQLAlchemy
        json_schema_extra={
            "example": {
                "id": 1,
                "codigo": "UEPB",
                "nome_completo": "Universidade Estadual da Paraíba",
                "nome_abreviado": "UEPB",
                "sigla": "UEPB",
                "tipo": "Estadual",
                "cnpj": "12.345.678/0001-90",
                "endereco": {
                    "logradouro": "Rua Baraúnas, 351",
                    "cidade": "Campina Grande",
                    "uf": "PB"
                },
                "contatos": {
                    "email_principal": "contato@uepb.edu.br"
                },
                "website": "https://uepb.edu.br",
                "ativo": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "endereco_completo": "Rua Baraúnas, 351 - Campina Grande - PB",
                "contato_principal": "contato@uepb.edu.br"
            }
        }
    )


# === SCHEMA PARA LISTAGEM ===
class InstituicaoList(BaseModel):
    """
    Schema para listagem paginada de instituições.

    Contém apenas campos essenciais para performance
    em listagens com muitos registros.
    """

    id: int
    codigo: str
    nome_abreviado: str
    sigla: str
    tipo: str
    ativo: bool
    total_programas: int = Field(
        0,
        description="Número total de programas da instituição"
    )

    model_config = ConfigDict(
        from_attributes=True
    )


# === SCHEMA PARA RESUMO/ESTATÍSTICAS ===
class InstituicaoResumo(BaseModel):
    """
    Schema para resumo estatístico da instituição.

    Usado em dashboards e relatórios gerenciais.
    """

    id: int
    codigo: str
    nome_abreviado: str
    tipo: str

    # Estatísticas
    total_programas: int = 0
    programas_ativos: int = 0
    total_docentes: int = 0
    total_discentes: int = 0

    # Última atividade
    ultima_atualizacao: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "codigo": "UEPB",
                "nome_abreviado": "UEPB",
                "tipo": "Estadual",
                "total_programas": 15,
                "programas_ativos": 14,
                "total_docentes": 120,
                "total_discentes": 350,
                "ultima_atualizacao": "2024-01-15T10:30:00Z"
            }
        }
    )