# app/schemas/docente.py
from __future__ import annotations

from datetime import date, datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------
# Literals (categorias controladas) — ajudam o front
# --------------------------------------------------------
TipoVinculo = Literal["Permanente", "Colaborador", "Visitante"]
RegimeTrabalho = Literal["DE", "40h", "20h"]
StatusDocente = Literal["Ativo", "Afastado", "Aposentado", "Desligado", "Falecido"]


# --------------------------------------------------------
# Base comum (campos compartilhados entre create/update/read)
# --------------------------------------------------------
class DocenteBase(BaseModel):
    """
    Campos que podem existir no Docente. No PATCH (merge-patch), qualquer campo:
    - ausente  => não altera
    - presente => atualiza
    - presente com null => seta NULL (se permitido na coluna)
    """

    # Identidade acadêmica e carreira
    matricula: Optional[str] = None
    categoria: Optional[str] = None                 # e.g., Titular, Associado, Adjunto...
    regime_trabalho: Optional[RegimeTrabalho] = None
    titulacao_maxima: Optional[str] = None
    instituicao_titulacao: Optional[str] = None
    ano_titulacao: Optional[int] = Field(default=None, ge=1900, le=2100)
    pais_titulacao: Optional[str] = None

    # Vínculo com o PPG
    tipo_vinculo: Optional[TipoVinculo] = None
    data_vinculacao: Optional[date] = None
    data_desvinculacao: Optional[date] = None

    # Métricas de pesquisa
    h_index: Optional[int] = Field(default=None, ge=0)
    total_publicacoes: Optional[int] = Field(default=None, ge=0)
    total_citacoes: Optional[int] = Field(default=None, ge=0)
    publicacoes_ultimos_5_anos: Optional[int] = Field(default=None, ge=0)

    # Orientações
    orientacoes_mestrado_andamento: Optional[int] = Field(default=None, ge=0)
    orientacoes_doutorado_andamento: Optional[int] = Field(default=None, ge=0)
    orientacoes_mestrado_concluidas: Optional[int] = Field(default=None, ge=0)
    orientacoes_doutorado_concluidas: Optional[int] = Field(default=None, ge=0)
    coorientacoes: Optional[int] = Field(default=None, ge=0)

    # Bolsa de produtividade
    bolsista_produtividade: Optional[bool] = None
    nivel_bolsa_produtividade: Optional[str] = None
    vigencia_bolsa_inicio: Optional[date] = None
    vigencia_bolsa_fim: Optional[date] = None

    # Perfil
    areas_interesse: Optional[str] = None
    projetos_atuais: Optional[str] = None
    curriculo_resumo: Optional[str] = None

    # Estado
    status: Optional[StatusDocente] = "Ativo"
    motivo_desligamento: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------
# CREATE — IDs obrigatórios (usuario_id, programa_id)
# --------------------------------------------------------
class DocenteCreate(DocenteBase):
    """
    Payload para criação de Docente.
    Observação: alguns campos de DocenteBase podem continuar None na criação.
    """
    usuario_id: int
    programa_id: int

    # Para criação, exigimos os mínimos de vínculo (opcional: você pode tornar obrigatórios)
    tipo_vinculo: TipoVinculo
    data_vinculacao: date


# --------------------------------------------------------
# UPDATE (PUT) — você decide a semântica:
#   - FULL (mais REST-estrito): exigir campos mínimos e substituir.
#   - PRAGMÁTICO (igual ao PATCH): aceitar parciais.
# Aqui vamos manter todos opcionais (pragmático), reaproveitando a mesma lógica do service.
# --------------------------------------------------------
class DocenteUpdate(DocenteBase):
    """PUT: por simplicidade, aceitamos parcial (igual ao PATCH).
    Se quiser modo FULL, torne obrigatórios os campos necessários aqui.
    """
    pass


# --------------------------------------------------------
# PATCH (merge-patch) — todos opcionais, tri-estado garantido no service
# --------------------------------------------------------
class DocentePatch(DocenteBase):
    """PATCH: JSON Merge Patch (RFC 7396).
    - ausente => não altera
    - presente com null => seta NULL
    - presente com valor => atualiza
    """
    pass


# --------------------------------------------------------
# READ — resposta completa para o front
# --------------------------------------------------------
class DocenteRead(DocenteBase):
    """Objeto retornado pela API após create/get/update/patch."""
    id: int
    usuario_id: int
    programa_id: int
    # Em Read, alguns campos que eram opcionais em Base você pode expor como obrigatórios
    # caso a regra do seu domínio garanta que existam após persistência.
    tipo_vinculo: Optional[TipoVinculo] = None
    data_vinculacao: Optional[date] = None

    created_at: datetime
    updated_at: datetime

# --------------------------------------------------------
# LIST — paginação amigável ao front
# --------------------------------------------------------
class DocenteList(BaseModel):
    """Retorno paginado de docentes para listagens no frontend."""
    items: List[DocenteRead]
    total: int
    limit: int
    offset: int

    model_config = ConfigDict(from_attributes=True)
