# app/api/routes/roles.py
from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.deps import get_db
from app.schemas.role import RoleCreate, RoleUpdate, RoleRead
from app.services.role_service import RoleService

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post(
    "",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar role",
)
def create_role(payload: RoleCreate, db: Session = Depends(get_db)) -> RoleRead:
    """Cria uma nova role (nome único)."""
    svc = RoleService(db)
    try:
        return svc.create(payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Violação de unicidade")


@router.get(
    "",
    response_model=List[RoleRead],
    summary="Listar roles",
)
def list_roles(db: Session = Depends(get_db)) -> List[RoleRead]:
    """Lista todas as roles."""
    svc = RoleService(db)
    items, _ = svc.list()
    return items


@router.get(
    "/{role_id}",
    response_model=RoleRead,
    summary="Obter role por ID",
)
def get_role(role_id: int, db: Session = Depends(get_db)) -> RoleRead:
    """Retorna uma role pelo ID."""
    svc = RoleService(db)
    obj = svc.get(role_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Role não encontrada")
    return obj


@router.put(
    "/{role_id}",
    response_model=RoleRead,
    summary="Atualizar role",
)
def update_role(role_id: int, payload: RoleUpdate, db: Session = Depends(get_db)) -> RoleRead:
    """Atualiza uma role existente."""
    svc = RoleService(db)
    obj = svc.update(role_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Role não encontrada")
    return obj


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_200_OK,
    summary="Remover role",
)
def delete_role(role_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    """Remove uma role pelo ID."""
    svc = RoleService(db)
    ok = svc.delete(role_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Role não encontrada")
    return {"detail": f"Role {role_id} removida com sucesso"}
