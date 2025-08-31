# app/routers/docentes.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db
from app.services.docente_service import DocenteService
from app.schemas.docente import (
    DocenteCreate,
    DocenteUpdate,
    DocenteRead,
    DocenteList,
)

router = APIRouter(prefix="/docentes", tags=["Docentes"])


# ----------------- CREATE -----------------
@router.post(
    "",
    response_model=DocenteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo docente",
)
def create_docente(payload: DocenteCreate, db: Session = Depends(get_db)) -> DocenteRead:
    return DocenteService(db).create_docente(payload)


# ----------------- READ (by ID) -----------------
@router.get(
    "/{docente_id}",
    response_model=DocenteRead,
    summary="Obter docente por ID",
)
def get_docente(
    docente_id: int = Path(..., ge=1, description="ID do docente"),
    db: Session = Depends(get_db),
) -> DocenteRead:
    return DocenteService(db).get_docente(docente_id)


# ----------------- LIST (paginação offset/limit) -----------------
@router.get(
    "",
    response_model=DocenteList,
    summary="Listar docentes paginados",
)
def list_docentes(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db),
) -> DocenteList:
    items, total = DocenteService(db).list_docentes(skip=skip, limit=limit)
    return DocenteList(
        items=[DocenteRead.model_validate(obj) for obj in items],
        total=total,
    )


# ----------------- UPDATE -----------------
@router.put(
    "/{docente_id}",
    response_model=DocenteRead,
    summary="Atualizar docente",
)
def update_docente(
    docente_id: int,
    payload: DocenteUpdate,
    db: Session = Depends(get_db),
) -> DocenteRead:
    return DocenteService(db).update_docente(docente_id, payload)


# ----------------- DELETE -----------------

@router.delete(
    "/{docente_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove um docente",
)
def delete_docente(
    docente_id: int = Path(..., ge=1, description="ID do docente"),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    service = DocenteService(db)
    ok = service.delete_docente(docente_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Docente não encontrado")
    return {"message": "Docente removido com sucesso"}

