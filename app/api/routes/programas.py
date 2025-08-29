from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional

from app.deps import get_db
from app.services.programa_service import ProgramaService
from app.schemas.programa import (
    ProgramaCreate,
    ProgramaUpdate,
    ProgramaRead,
    ProgramaList,
)

router = APIRouter(prefix="/programas", tags=["programas"])


# ----------------- CREATE -----------------
@router.post(
    "",
    response_model=ProgramaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo programa",
)
def create_programa(payload: ProgramaCreate, db: Session = Depends(get_db)):
    service = ProgramaService(db)
    return service.create_programa(payload)


# ----------------- READ -----------------
@router.get(
    "/{programa_id}",
    response_model=ProgramaRead,
    summary="Obter programa por ID",
)
def get_programa(programa_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    service = ProgramaService(db)
    obj = service.get_programa(programa_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    return obj


@router.get(
    "",
    response_model=ProgramaList,
    summary="Listar programas paginados",
)
def list_programas(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> ProgramaList:
    service = ProgramaService(db)
    items, total = service.list_programas(limit=limit, offset=offset)
    return ProgramaList(
        items=[ProgramaRead.model_validate(obj) for obj in items],
        total=total,
    )


# ----------------- UPDATE -----------------
@router.put(
    "/{programa_id}",
    response_model=ProgramaRead,
    summary="Atualizar um programa (PUT)",
)
def update_programa(programa_id: int, payload: ProgramaUpdate, db: Session = Depends(get_db)):
    service = ProgramaService(db)
    return service.update_programa(programa_id, payload)


# ----------------- DELETE -----------------
@router.delete(
    "/{programa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover programa",
)
def delete_programa(programa_id: int, db: Session = Depends(get_db), hard: bool = False):
    service = ProgramaService(db)
    ok = service.delete_programa(programa_id, hard=hard)
    if not ok:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    return None


# app/api/routes/programas.py

@router.delete(
    "/{programa_id}/usuarios/{usuario_id}",
    status_code=status.HTTP_200_OK,
    summary="Desvincular um usuário de um programa",
)
def desvincular_usuario_programa(
    programa_id: int,
    usuario_id: int,
    db: Session = Depends(get_db),
):
    service = UsuarioProgramaRoleService(db)
    ok = service.desvincular_usuario_programa(usuario_id, programa_id)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail="Vínculo usuário-programa não encontrado"
        )
    return {"message": "Usuário desvinculado do programa com sucesso"}
