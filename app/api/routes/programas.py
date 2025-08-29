from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlalchemy.orm import Session
from app.deps import get_db
from app.services.usuario_programa_service import UsuarioProgramaService

router = APIRouter(prefix="/programas", tags=["programas"])

@router.delete(
    "/{programa_id}/membros/{assoc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,  # <- evita JSONResponse (sem body)
)
def desativar_vinculo(programa_id: int, assoc_id: int, db: Session = Depends(get_db)) -> Response:
    """
    Desativa (soft delete) o vínculo usuário–programa.
    Retorna 204 sem corpo conforme o HTTP.
    """
    svc = UsuarioProgramaService(db)
    assoc = svc.desativar(assoc_id)
    if not assoc:
        # 404 ainda é permitido (com body), pois não conflita com o 204 desta rota.
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")
    # 204 não pode ter body:
    return Response(status_code=status.HTTP_204_NO_CONTENT)
