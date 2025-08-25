from __future__ import annotations

from typing import Sequence

from sqlalchemy.orm import Session

from app.repositories.instituicao_repo import InstituicaoRepository
from app.schemas.instituicao import (
    InstituicaoCreate, InstituicaoUpdate, InstituicaoRead, InstituicaoList
)
from app.models.instituicao import Instituicao


def _format_endereco(endereco: dict | None) -> str:
    if not endereco:
        return ""
    log = endereco.get("logradouro")
    cid = endereco.get("cidade")
    uf = endereco.get("uf")
    cep = endereco.get("cep")
    parts = [p for p in [log, cid, uf] if p]
    base = " - ".join(parts) if parts else ""
    if cep:
        base = f"{base} ({cep})" if base else f"{cep}"
    return base


def _contato_principal(contatos: dict | None) -> str:
    if not contatos:
        return ""
    return contatos.get("email_principal") or contatos.get("telefone_principal") or ""


class InstituicaoService:
    """Regras de negócio para Instituição."""

    def __init__(self, db: Session) -> None:
        self.repo = InstituicaoRepository(db)

    def create(self, payload: InstituicaoCreate) -> Instituicao:
        # Evita duplicidade por 'codigo' e 'sigla'
        if self.repo.get_by_codigo(payload.codigo):
            raise ValueError("Código já cadastrado para outra instituição.")
        if self.repo.get_by_sigla(payload.sigla):
            raise ValueError("Sigla já cadastrada para outra instituição.")
        return self.repo.create(payload.model_dump(exclude_unset=True))

    def get(self, instituicao_id: int) -> Instituicao | None:
        return self.repo.get(instituicao_id)

    def list(self, *, limit: int = 50, offset: int = 0, only_active: bool = False) -> tuple[list[InstituicaoList], int]:
        objs = self.repo.list(limit=limit, offset=offset, only_active=only_active)
        total = self.repo.count(only_active=only_active)
        items = [InstituicaoList.model_validate(o) for o in objs]
        return items, total

    def update(self, instituicao_id: int, payload: InstituicaoUpdate) -> Instituicao:
        obj = self.repo.get(instituicao_id)
        if not obj:
            raise LookupError("Instituição não encontrada.")
        data = payload.model_dump(exclude_unset=True)
        # Valida unicidade se código/sigla foram informados
        if "codigo" in data:
            other = self.repo.get_by_codigo(data["codigo"])
            if other and other.id != instituicao_id:
                raise ValueError("Código já cadastrado para outra instituição.")
        if "sigla" in data:
            other = self.repo.get_by_sigla(data["sigla"])
            if other and other.id != instituicao_id:
                raise ValueError("Sigla já cadastrada para outra instituição.")
        return self.repo.update(obj, data)

    def delete(self, instituicao_id: int) -> None:
        obj = self.repo.get(instituicao_id)
        if not obj:
            return
        self.repo.delete(obj)

    def to_read(self, obj: Instituicao) -> InstituicaoRead:
        """Mapeia ORM -> Schema de leitura com campos computados."""
        endereco_completo = _format_endereco(obj.endereco)
        contato = _contato_principal(obj.contatos)
        base = InstituicaoRead.model_validate(obj)
        # sobrescreve computados
        base.endereco_completo = endereco_completo
        base.contato_principal = contato
        return base
