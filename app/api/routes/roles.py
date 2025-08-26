from __future__ import annotations
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.services.role_service import RoleService
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut

from app.schemas.role import (RoleCreate, RoleUpdate, RoleOut)

# Prefixo para todos os endpoints desta rota
router = APIRouter(prefix="/roles", tags=["roles"])


# ----------------- CREATE -----------------
@router.post(
    "",
    response_model=RoleOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar uma nova role",
)
def create_role(payload: RoleCreate, db: Session = Depends(get_session)):
    """
    Cria uma nova role no sistema.

    - Request body validado via **RoleCreate**.
    - Retorna a role criada no formato **RoleOut**.
    """
    service = RoleService(db)
    return service.create_role(payload)


# ----------------- READ -----------------
@router.get(
    "/{role_id}",
    response_model=RoleOut,
    summary="Obter role por ID",
)
def get_role(role_id: int, db: Session = Depends(get_session)):
    """
    Retorna uma role pelo seu ID.

    - Se não for encontrada, lança **404 Not Found**.
    """
    service = RoleService(db)
    role = service.get_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role não encontrada")
    return role


@router.get(
    "/by-nome/{nome}",
    response_model=RoleOut,
    summary="Obter role por nome",
)
def get_role_by_nome(nome: str, db: Session = Depends(get_session)):
    """
    Retorna uma role pelo nome (único no sistema).

    - Se não for encontrada, lança **404 Not Found**.
    """
    service = RoleService(db)
    role = service.get_role_by_nome(nome)
    if not role:
        raise HTTPException(status_code=404, detail="Role não encontrada")
    return role


@router.get(
    "",
    response_model=Dict[str, Any],
    summary="Listar roles paginadas",
)
def list_roles(
    db: Session = Depends(get_session),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de registros por página"),
    offset: int = Query(0, ge=0, description="Deslocamento inicial (página atual)"),
    search: Optional[str] = Query(None, description="Filtro por nome"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo/inativo"),
):
    """
    Lista roles do sistema com suporte a paginação e filtros.

    Retorna no formato:

    ```json
    {
      "items": [...],
      "total": 123
    }
    ```
    """
    service = RoleService(db)
    items, total = service.list_roles(limit=limit, offset=offset, search=search, ativo=ativo)
    return {"items": items, "total": total}


@router.get(
    "/all",
    response_model=List[RoleOut],
    summary="Listar todas as roles (sem paginação)",
)
def list_all_roles(db: Session = Depends(get_session)):
    """
    Lista todas as roles existentes no sistema.
    """
    service = RoleService(db)
    return service.list_all_roles()


# ----------------- UPDATE -----------------
@router.put(
    "/{role_id}",
    response_model=RoleOut,
    summary="Atualizar uma role existente",
)
def update_role(role_id: int, payload: RoleUpdate, db: Session = Depends(get_session)):
    """
    Atualiza parcialmente uma role existente.

    - Se a role não existir, lança **404 Not Found**.
    """
    service = RoleService(db)
    try:
        return service.update_role(role_id, payload)
    except ValueError:
        raise HTTPException(status_code=404, detail="Role não encontrada")


# ----------------- DELETE -----------------
@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover uma role",
)
def delete_role(role_id: int, db: Session = Depends(get_session), hard: bool = False):
    """
    Remove uma role existente.

    - `hard=True` → exclui definitivamente do banco.
    - `hard=False` (default) → apenas faz soft delete (`ativo=False`).
    """
    service = RoleService(db)
    service.delete_role(role_id, hard=hard)
    return None
