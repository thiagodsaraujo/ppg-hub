# tests/test_roles.py
from __future__ import annotations
from sqlalchemy.orm import Session
from app.repositories.role_repo import RoleRepository

def ensure_role(repo: RoleRepository, data: dict):
    """Cria a role se não existir; idempotente por nome."""
    existing = repo.get_by_nome(data["nome"]) if hasattr(repo, "get_by_nome") else None
    return existing or repo.create(data)

class TestRoles:
    """Testes de integração para Roles (CRUD mínimo + listagem)."""

    def test_create_and_get_role(self, db_session: Session):
        repo = RoleRepository(db_session)
        payload = {
            "nome": "Discente",
            "descricao": "Discente padrão",
            "nivel_acesso": 1,
            "permissoes": {"view_courses": True},
            "ativo": True,
        }
        role = ensure_role(repo, payload)
        assert role.id is not None
        assert role.nome == "coordenador"

        fetched = repo.get_by_nome("coordenador")
        assert fetched is not None
        assert fetched.nivel_acesso == 3

    def test_list_all_roles(self, db_session: Session):
        repo = RoleRepository(db_session)
        roles = repo.list_all()
        # sempre retorna uma lista
        assert isinstance(roles, list)
        # se houver itens, devem ter id e nome
        assert all(hasattr(r, "id") and hasattr(r, "nome") for r in roles)
