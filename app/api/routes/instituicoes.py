from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.session import get_session
from app.models.instituicao import Instituicao
from app.schemas.instituicao import (
    InstituicaoCreate,
    InstituicaoRead,
    InstituicaoList,
)

router = APIRouter(prefix="/instituicoes", tags=["instituicoes"])

@router.post(
    "",
    response_model=InstituicaoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar instituição",
)
def create_instituicao(payload: InstituicaoCreate, db: Session = Depends(get_session)) -> InstituicaoRead:
    """
    Usa schema **InstituicaoCreate** para validar o body e **InstituicaoRead** para padronizar a resposta.
    - FastAPI valida e retorna **422** se `tipo`, `cnpj`, etc. estiverem inválidos.
    - Tratamos **IntegrityError** para devolver **409** em caso de duplicidade (codigo/sigla/cnpj).
    """
    obj = Instituicao(**payload.model_dump())
    db.add(obj)
    try:
        db.flush()      # garante `obj.id`
        db.commit()     # persiste (ajuste se sua get_session já commita no finally)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Violação de unicidade (código/sigla/cnpj).")

    # Como `InstituicaoRead` tem from_attributes=True, dá para devolver o ORM direto:
    return InstituicaoRead.model_validate(obj)

@router.get(
    "",
    response_model=List[InstituicaoList],
    summary="Listar instituições",
)
def list_instituicoes(db: Session = Depends(get_session)) -> list[InstituicaoList]:
    """
    Devolve uma **lista tipada** com campos próprios para listagem (enxuto e consistente).
    """
    rows = db.scalars(select(Instituicao).order_by(Instituicao.id)).all()
    return [InstituicaoList.model_validate(r) for r in rows]
