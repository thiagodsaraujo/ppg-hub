from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_session

from app.schemas.instituicao import (
    InstituicaoCreate,
    InstituicaoUpdate,
    InstituicaoRead,
    InstituicaoList,
)
from app.services.instituicao_service import InstituicaoService

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
def update_instituicao(instituicao_id: int, payload: InstituicaoUpdate, db: Session = Depends(get_session)):
    service = InstituicaoService(db)
    obj = service.update(instituicao_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    return InstituicaoRead.model_validate(obj)


@router.delete("/{instituicao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_instituicao(instituicao_id: int, db: Session = Depends(get_session)):
    service = InstituicaoService(db)
    deleted = service.delete(instituicao_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    return None
