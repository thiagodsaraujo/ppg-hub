from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.deps import get_db
from app.services.instituicao_service import InstituicaoService
from app.schemas.instituicao import (
    InstituicaoCreate,
    InstituicaoUpdate,
    InstituicaoPut,
    InstituicaoRead,
    InstituicaoList,
)

router = APIRouter(prefix="/instituicoes", tags=["instituicoes"])


@router.post(
    "",
    response_model=InstituicaoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma instituição",
)
def create_instituicao(
    payload: InstituicaoCreate,
    db: Session = Depends(get_db),
) -> InstituicaoRead:
    service = InstituicaoService(db)  # ✅ passa a Session
    try:
        obj = service.create(payload.model_dump())
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Violação de unicidade")
    return InstituicaoRead.model_validate(obj)


@router.get(
    "",
    response_model=InstituicaoList,
    summary="Lista instituições paginadas (limit/offset)",
)
def list_instituicoes(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> InstituicaoList:
    service = InstituicaoService(db)  # ✅
    items, total = service.list(limit, offset)
    return InstituicaoList(
        items=[InstituicaoRead.model_validate(obj) for obj in items],
        total=total,
    )


@router.get(
    "/{instituicao_id}",
    response_model=InstituicaoRead,
    summary="Obtém instituição por ID",
)
def get_instituicao(
    instituicao_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
) -> InstituicaoRead:
    service = InstituicaoService(db)  # ✅
    obj = service.get(instituicao_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    return InstituicaoRead.model_validate(obj)


@router.put(
    "/{instituicao_id}",
    response_model=InstituicaoRead,
    status_code=status.HTTP_200_OK,
    summary="Atualiza instituição (substituição total)",
)
def put_instituicao(
    instituicao_id: int = Path(..., ge=1),
    payload: InstituicaoPut = ...,
    db: Session = Depends(get_db),
) -> InstituicaoRead:
    service = InstituicaoService(db)  # ✅
    try:
        obj = service.put(instituicao_id, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Violação de unicidade")
    return InstituicaoRead.model_validate(obj)


@router.patch(
    "/{instituicao_id}",
    response_model=InstituicaoRead,
    summary="Atualização parcial da instituição",
)
def patch_instituicao(
    instituicao_id: int = Path(..., ge=1),
    payload: InstituicaoUpdate = ...,
    db: Session = Depends(get_db),
) -> InstituicaoRead:
    service = InstituicaoService(db)  # ✅
    try:
        obj = service.patch(instituicao_id, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Violação de unicidade")
    if not obj:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    return InstituicaoRead.model_validate(obj)


@router.delete(
    "/{instituicao_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove uma instituição",
)
def delete_instituicao(
    instituicao_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    service = InstituicaoService(db)  # ✅
    ok = service.delete(instituicao_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    return {"message": "Instituição removida com sucesso"}
