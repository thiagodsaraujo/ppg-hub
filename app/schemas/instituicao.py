from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict, HttpUrl, field_validator


# ================================
# SCHEMAS BASE
# ================================
class InstituicaoBase(BaseModel):
    """Campos comuns da Instituição (usados em entrada e saída).

    Por que importa:
      - Define o "contrato" mínimo de dados de Instituição.
      - Aplica validações de tamanho/formato logo na borda da API.
      - Serve para herança em Create/Read, evitando duplicação.
    """

    # Identificadores e nomes
    codigo: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="Código único (UEPB, UFCG). Usado como chave de negócio.",
        example="UEPB",
    )
    nome_completo: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Nome oficial da instituição.",
        example="Universidade Estadual da Paraíba",
    )
    nome_abreviado: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Nome abreviado para telas/documentos.",
        example="UEPB",
    )
    sigla: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="Sigla institucional.",
        example="UEPB",
    )
    tipo: str = Field(
        ...,
        description="Tipo da instituição (ex.: Federal, Estadual, Municipal, Privada).",
        example="Estadual",
    )

    # Dados cadastrais opcionais
    cnpj: Optional[str] = Field(
        None,
        min_length=14,
        max_length=18,
        description="CNPJ (com ou sem formatação).",
        example="12.345.678/0001-90",
    )
    natureza_juridica: Optional[str] = Field(
        None,
        max_length=100,
        description="Natureza jurídica (ex.: Autarquia Estadual).",
        example="Autarquia Estadual",
    )

    # Blocos flexíveis (JSON) — bom para evoluir sem migrar o schema toda hora
    endereco: Optional[Dict[str, Any]] = Field(
        None,
        description="Endereço em JSON (estrutura flexível).",
        example={
            "logradouro": "Rua Baraúnas, 351",
            "bairro": "Universitário",
            "cidade": "Campina Grande",
            "uf": "PB",
            "cep": "58429-500",
            "complemento": "Campus I",
        },
    )
    contatos: Optional[Dict[str, Any]] = Field(
        None,
        description="Contatos em JSON (email/telefone).",
        example={
            "email_principal": "contato@uepb.edu.br",
            "telefone_principal": "(83) 3315-3300",
            "emails": ["contato@uepb.edu.br"],
            "telefones": ["(83) 3315-3300"],
        },
    )
    redes_sociais: Optional[Dict[str, Any]] = Field(
        None,
        description="URLs de redes sociais (estrutura livre).",
        example={
            "facebook": "https://facebook.com/uepb.oficial",
            "instagram": "https://instagram.com/uepb.oficial",
        },
    )

    # Metadados e integrações
    logo_url: Optional[HttpUrl] = Field(None, description="URL do logotipo (http/https).")
    website: Optional[HttpUrl] = Field(None, description="Site oficial (http/https).")
    fundacao: Optional[datetime] = Field(None, description="Data de fundação (ISO8601).")
    openalex_institution_id: Optional[str] = Field(
        None, description="ID da instituição no OpenAlex.", example="I123456789"
    )
    ror_id: Optional[str] = Field(
        None, description="ROR ID (pode ser a URL ror.org ou apenas o código).", example="https://ror.org/01234567"
    )

    # Estado e preferências
    ativo: bool = Field(True, description="Se a instituição está ativa (soft-state).")
    configuracoes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configurações diversas (tema, idioma, timezone, flags).",
        example={"cor_tema": "#0066cc", "timezone": "America/Sao_Paulo", "idioma_padrao": "pt-BR"},
    )

    # Permite criar este schema a partir de um objeto ORM (atributos)
    model_config = ConfigDict(from_attributes=True)


# ================================
# SCHEMA PARA CRIAÇÃO
# ================================
class InstituicaoCreate(InstituicaoBase):
    """Payload para criar Instituição (entrada de POST).

    Observações:
      - Herda todas as validações do Base.
      - Adiciona validadores específicos de negócio (tipo, CNPJ, código).
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
                    "cep": "58429-500",
                },
                "contatos": {
                    "email_principal": "contato@uepb.edu.br",
                    "telefone_principal": "(83) 3315-3300",
                },
                "website": "https://uepb.edu.br",
                "fundacao": "1987-04-05T00:00:00",
                "ativo": True,
            }
        }
    )

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        """Restringe o tipo a um conjunto conhecido.
        Por que importa: garante consistência nas telas/filtros e KPIs.
        """
        tipos_validos = ["Federal", "Estadual", "Municipal", "Privada"]
        if v not in tipos_validos:
            raise ValueError(f"Tipo deve ser um de: {', '.join(tipos_validos)}")
        return v

    @field_validator("cnpj")
    @classmethod
    def validar_cnpj_formato(cls, v: Optional[str]) -> Optional[str]:
        """Aceita CNPJ com/sem formatação, normaliza e valida 14 dígitos.
        Por que importa: evita guardar lixo e facilita consultas/integrações.
        """
        if v is None:
            return v
        cnpj_limpo = v.replace(".", "").replace("/", "").replace("-", "")
        if len(cnpj_limpo) != 14 or not cnpj_limpo.isdigit():
            raise ValueError("CNPJ deve ter 14 dígitos numéricos")
        # retorna já formatado (padrão único na base)
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"

    @field_validator("codigo")
    @classmethod
    def validar_codigo_formato(cls, v: str) -> str:
        """Normaliza o código (trim + uppercase) e restringe o charset.
        Por que importa: `codigo` funciona como chave de negócio e aparece em URLs/UI.
        """
        codigo_limpo = v.strip().upper()
        if not codigo_limpo.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Código deve conter apenas letras, números, _ ou -")
        return codigo_limpo


# ================================
# SCHEMA PARA ATUALIZAÇÃO (PATCH)
# ================================
class InstituicaoUpdate(BaseModel):
    """Atualização parcial (PATCH). Todos os campos são opcionais.

    Por que importa:
      - Permite mudanças incrementais sem exigir reenvio do objeto inteiro.
      - Reaproveita validadores críticos do Create para manter a consistência.
    """

    codigo: Optional[str] = Field(None, min_length=2, max_length=20)
    nome_completo: Optional[str] = Field(None, min_length=5, max_length=500)
    nome_abreviado: Optional[str] = Field(None, min_length=2, max_length=50)
    sigla: Optional[str] = Field(None, min_length=2, max_length=10)
    tipo: Optional[str] = Field(None)
    cnpj: Optional[str] = Field(None)
    natureza_juridica: Optional[str] = Field(None, max_length=100)
    endereco: Optional[Dict[str, Any]] = Field(None)
    contatos: Optional[Dict[str, Any]] = Field(None)
    redes_sociais: Optional[Dict[str, Any]] = Field(None)
    logo_url: Optional[HttpUrl] = Field(None)
    website: Optional[HttpUrl] = Field(None)
    fundacao: Optional[datetime] = Field(None)
    openalex_institution_id: Optional[str] = Field(None)
    ror_id: Optional[str] = Field(None)
    ativo: Optional[bool] = Field(None)
    configuracoes: Optional[Dict[str, Any]] = Field(None)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome_abreviado": "UEPB - Campus II",
                "contatos": {"telefone_principal": "(83) 3315-3400"},
                "configuracoes": {"cor_tema": "#ff6600"},
            }
        }
    )

    # Reuso dos validadores do Create (boa prática: DRY e consistência)
    _validar_tipo = field_validator("tipo")(InstituicaoCreate.validar_tipo.__func__)
    _validar_cnpj = field_validator("cnpj")(InstituicaoCreate.validar_cnpj_formato.__func__)
    _validar_codigo = field_validator("codigo")(InstituicaoCreate.validar_codigo_formato.__func__)


# ================================
# SCHEMAS DE SAÍDA
# ================================
class InstituicaoRead(InstituicaoBase):
    """Resposta completa da API (GET), incluindo IDs e campos derivados."""

    id: int = Field(..., description="ID único no banco.")
    created_at: datetime = Field(..., description="Data/hora de criação (server).")
    updated_at: datetime = Field(..., description="Data/hora da última atualização (server).")

    # Estes campos são “derivados”. Você pode preenchê-los no service
    # ou calcular com @computed_field (Pydantic v2) se quiser.
    endereco_completo: str = Field("", description="Endereço formatado completo.")
    contato_principal: str = Field("", description="Email/Telefone principal.")


class InstituicaoList(BaseModel):
    """Linha de listagem: resposta enxuta para tabelas/list views."""

    id: int
    codigo: str
    nome_abreviado: str
    sigla: str
    tipo: str
    ativo: bool
    total_programas: int = Field(0, description="Quantidade de programas ligados à instituição.")

    model_config = ConfigDict(from_attributes=True)


class InstituicaoResumo(BaseModel):
    """Resumo/estatísticas para dashboards e cards."""

    id: int
    codigo: str
    nome_abreviado: str
    tipo: str
    total_programas: int = 0
    programas_ativos: int = 0
    total_docentes: int = 0
    total_discentes: int = 0
    ultima_atualizacao: datetime

    model_config = ConfigDict(from_attributes=True)
