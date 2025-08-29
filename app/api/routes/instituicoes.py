from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.deps import get_db  # <- único ponto para injetar sessão
from app.repositories.instituicao_repo import InstituicaoRepository
from app.services.instituicao_service import InstituicaoService

from app.schemas.instituicao import (
    InstituicaoCreate,
    InstituicaoUpdate,
    InstituicaoPut,    # <- garantir que existe no seu schemas
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
    """Cria e retorna a Instituição. Conflitos de unicidade retornam 409."""
    service = InstituicaoService(InstituicaoRepository(db))
    try:
        obj = service.create(payload.model_dump())
        # regra de transação ideal: commit dentro da service (recomendado)
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
    """Lista paginada com validação de parâmetros."""
    service = InstituicaoService(InstituicaoRepository(db))
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
    """Busca por ID; retorna 404 se não existir."""
    service = InstituicaoService(InstituicaoRepository(db))
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
    """PUT substitui totalmente; retorna 409 em conflito de UNIQUE."""
    service = InstituicaoService(InstituicaoRepository(db))
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
    """PATCH parcial; retorna 409 em conflito e 404 se não existir."""
    service = InstituicaoService(InstituicaoRepository(db))
    try:
        obj = service.patch(instituicao_id, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Violação de unicidade")
    return InstituicaoRead.model_validate(obj)


@router.delete(
    "/{instituicao_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove uma instituição",
)
async def delete_instituicao(instituicao_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    service = InstituicaoService(db)
    service.delete(instituicao_id)
    return {"message": "Instituição removida com sucesso"}

