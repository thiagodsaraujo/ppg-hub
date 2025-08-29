from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
import datetime, socket

from app.deps import get_db

router = APIRouter(prefix="", tags=["monitoring"])


@router.get("/healthz2")
def healthz() -> dict[str, str]:
    """
    Health check básico da aplicação.
    - Apenas retorna status `ok`.
    """
    return {"status": "ok"}


@router.get("/readyz")
def readyz(db: Session = Depends(get_db)) -> dict[str, str]:
    """
    Readiness check.
    Verifica se a API está viva e se o banco responde a um ping simples.
    """
    health: dict[str, str] = {
        "app_status": "ok",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "hostname": socket.gethostname(),
    }
    try:
        # ping no BD; .scalar() força execução e leitura
        db.scalar(text("SELECT 1"))
        health["database"] = "connected"
    except Exception as e:
        # se você já registrou handlers globais, pode relançar; aqui devolvemos status legível
        health["database"] = f"error: {e.__class__.__name__}: {e}"
    return health
