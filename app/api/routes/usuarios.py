from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_session
from app.services.usuario_service import UsuarioService
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioOut


# Prefixo / tag para Swagger
router = APIRouter(prefix="/usuarios", tags=["usuarios"])


# ----------------- CREATE -----------------
@router.post(
    "",
    response_model=UsuarioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo usuário",
)
def create_usuario(payload: UsuarioCreate, db: Session = Depends(get_session)):
    """
    Cria um novo usuário no sistema.

    - **email** deve ser único
    - **senha** será armazenada com hash (não em texto puro)
    - **role_id** deve existir na tabela de roles
    """
    service = UsuarioService(db)
    try:
        return service.create(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ----------------- READ -----------------
@router.get(
    "/{usuario_id}",
    response_model=UsuarioOut,
    summary="Obter usuário por ID",
)
def get_usuario(usuario_id: int, db: Session = Depends(get_session)):
    """
    Retorna um usuário pelo seu **ID**.
    """
    service = UsuarioService(db)
    obj = service.get(usuario_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return obj


@router.get(
    "",
    response_model=List[UsuarioOut],
    summary="Listar usuários paginados",
)
def list_usuarios(
    db: Session = Depends(get_session),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros por página"),
    offset: int = Query(0, ge=0, description="Deslocamento inicial (página atual)"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo/inativo"),
):
    """
    Lista usuários com suporte a paginação e filtros.
    """
    service = UsuarioService(db)
    items, _ = service.list(limit=limit, offset=offset, ativo=ativo)
    return items


# ----------------- UPDATE -----------------
@router.put(
    "/{usuario_id}",
    response_model=UsuarioOut,
    summary="Atualizar um usuário",
)
def update_usuario(usuario_id: int, payload: UsuarioUpdate, db: Session = Depends(get_session)):
    """
    Atualiza parcialmente um usuário existente.

    - Se o usuário não existir, retorna **404**.
    """
    service = UsuarioService(db)
    try:
        return service.update(usuario_id, payload)
    except ValueError:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")


# ----------------- DELETE -----------------
@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover usuário",
)
def delete_usuario(usuario_id: int, db: Session = Depends(get_session), hard: bool = False):
    """
    Remove um usuário do sistema.

    - `hard=True` → exclui definitivamente do banco
    - `hard=False` → apenas faz soft delete (`ativo=False`)
    """
    service = UsuarioService(db)
    service.delete(usuario_id, hard=hard)
    return None
