from __future__ import annotations
from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.instituicao import Instituicao

class InstituicaoRepository:
    """Opera o CRUD/consultas de `Instituicao` isolando SQLAlchemy da camada de serviço.

    Por que separar?
      - Testabilidade: você "finge" o repo em testes do service.
      - Manutenibilidade: troque SQL sem mexer na API.
      - Clareza: service decide regras; repo só acessa dados.
    """

    def __init__(self, db: Session) -> None:
        # A Session é fornecida pela dependência (FastAPI) — 1 por request.
        self.db = db

    def create(self, data: dict) -> Instituicao:
        """Cria e retorna a entidade (com `id` já preenchido).

        Usamos `flush()` (e não `commit()`) para:
          - Forçar o INSERT e preencher `obj.id` (chave gerada).
          - Deixar o commit sob controle da camada superior (service ou dep).
        """
        obj = Instituicao(**data)
        self.db.add(obj)
        self.db.flush()  # INSERT imediato na transação corrente
        return obj

    def get(self, instituicao_id: int) -> Instituicao | None:
        """Busca por PK. Retorna None se não existir (não levanta exceção)."""
        return self.db.get(Instituicao, instituicao_id)

    def get_by_codigo(self, codigo: str) -> Instituicao | None:
        """Busca por `codigo` (chave de negócio)."""
        stmt = select(Instituicao).where(Instituicao.codigo == codigo)
        # `scalar` retorna único elemento ou None, evitando `scalar_one()` (que lança erro)
        return self.db.scalar(stmt)

    def get_by_sigla(self, sigla: str) -> Instituicao | None:
        """Busca por `sigla` (única)."""
        stmt = select(Instituicao).where(Instituicao.sigla == sigla)
        return self.db.scalar(stmt)

    def list(self, *, limit: int = 50, offset: int = 0, only_active: bool = False) -> Sequence[Instituicao]:
        """Lista entidades com paginação simples e filtro opcional `ativo=True`."""
        stmt = select(Instituicao).offset(offset).limit(limit)
        if only_active:
            stmt = stmt.where(Instituicao.ativo.is_(True))
        # `scalars()` transforma o result em iterável de objetos ORM
        return self.db.scalars(stmt).all()

    def count(self, *, only_active: bool = False) -> int:
        """Retorna contagem total (ou apenas ativos)."""
        stmt = select(func.count()).select_from(Instituicao)
        if only_active:
            stmt = stmt.where(Instituicao.ativo.is_(True))
        # `scalar` pode retornar None dependendo do dialect; garanta int
        return int(self.db.scalar(stmt) or 0)

    def update(self, obj: Instituicao, data: dict) -> Instituicao:
        """Aplica alterações campo a campo e `flush()`.

        Observação:
          - `data` deve conter apenas campos permitidos (faça o filtro no service).
          - Após `flush()`, `obj` já reflete o estado atual no DB (na mesma transação).
        """
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.add(obj)   # opcional; garante que está na sessão
        self.db.flush()
        return obj

    def delete(self, obj: Instituicao) -> None:
        """Remove fisicamente (DELETE) e `flush()` imediatamente.

        Em domínios com auditoria forte, você pode preferir 'soft delete'
        (ex.: `obj.ativo = False`) e manter histórico.
        """
        self.db.delete(obj)
        self.db.flush()
