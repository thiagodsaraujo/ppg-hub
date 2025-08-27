from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_session, get_db
from app.repositories.instituicao_repo import InstituicaoRepository
from app.services.instituicao_service import InstituicaoService

from app.schemas.instituicao import (
    InstituicaoCreate,
    InstituicaoUpdate,
    InstituicaoRead,
    InstituicaoList,
)


router = APIRouter(prefix="/instituicoes", tags=["instituicoes"])


@router.post("", response_model=InstituicaoRead, status_code=status.HTTP_201_CREATED)
def create_instituicao(payload: InstituicaoCreate, db: Session = Depends(get_session)):
    service = InstituicaoService(db)
    try:
        obj = service.create(payload.model_dump())
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Violação de unicidade")
    return InstituicaoRead.model_validate(obj)


@router.get("", response_model=InstituicaoList)
def list_instituicoes(db: Session = Depends(get_session), limit: int = 10, offset: int = 0):
    service = InstituicaoService(db)
    items, total = service.list(limit, offset)
    return InstituicaoList(
        items=[InstituicaoRead.model_validate(obj) for obj in items],
        total=total,
    )


@router.get("/{instituicao_id}", response_model=InstituicaoRead)
def get_instituicao(instituicao_id: int, db: Session = Depends(get_session)):
    service = InstituicaoService(db)
    obj = service.get(instituicao_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    return InstituicaoRead.model_validate(obj)

@router.put("/{instituicao_id}", response_model=InstituicaoRead)
def put_instituicao(
    instituicao_id: int = Path(..., ge=1),
    payload: InstituicaoPut = ...,
    db: Session = Depends(get_db),
) -> InstituicaoRead:
    service = InstituicaoService(InstituicaoRepository(db))
    return service.put(instituicao_id, payload)

@router.patch("/{instituicao_id}", response_model=InstituicaoRead)
def patch_instituicao(
    instituicao_id: int = Path(..., ge=1),
    payload: InstituicaoUpdate = ...,
    db: Session = Depends(get_db),
) -> InstituicaoRead:
    service = InstituicaoService(InstituicaoRepository(db))
    return service.patch(instituicao_id, payload)


@router.delete("/{instituicao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_instituicao(instituicao_id: int, db: Session = Depends(get_session)):
    service = InstituicaoService(db)
    deleted = service.delete(instituicao_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    return None
