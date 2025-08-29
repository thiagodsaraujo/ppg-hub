from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional

from app.deps import get_db
from app.services.usuario_service import UsuarioService
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioRead, UsuarioList


router = APIRouter(prefix="/usuarios", tags=["usuarios"])


# ----------------- CREATE -----------------
@router.post(
    "",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo usuário",
)
def create_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    service = UsuarioService(db)
    try:
        return service.create_usuario(payload)  # ✅ método correto no service
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ----------------- READ -----------------
@router.get(
    "/{usuario_id}",
    response_model=UsuarioRead,
    summary="Obter usuário por ID",
)
def get_usuario(usuario_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    service = UsuarioService(db)
    obj = service.get_usuario(usuario_id)  # ✅ método correto
    if not obj:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return obj


@router.get(
    "",
    response_model=UsuarioList,
    summary="Listar usuários paginados",
)
def list_usuarios(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    ativo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
) -> UsuarioList:
    service = UsuarioService(db)
    items, total = service.list_usuarios(limit=limit, offset=offset, ativo=ativo)  # ✅ método correto
    return UsuarioList(
        items=[UsuarioRead.model_validate(obj) for obj in items],
        total=total,
    )


# ----------------- UPDATE -----------------
@router.put(
    "/{usuario_id}",
    response_model=UsuarioRead,
    summary="Atualizar um usuário",
)
def update_usuario(usuario_id: int, payload: UsuarioUpdate, db: Session = Depends(get_db)):
    service = UsuarioService(db)
    obj = service.update_usuario(usuario_id, payload)  # ✅ método correto
    if not obj:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return obj


# ----------------- DELETE -----------------
@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover usuário",
)
def delete_usuario(usuario_id: int, db: Session = Depends(get_db), hard: bool = False):
    service = UsuarioService(db)
    ok = service.delete_usuario(usuario_id, hard=hard)  # ✅ método correto
    if not ok:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return None
