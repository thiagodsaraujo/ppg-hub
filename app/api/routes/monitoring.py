from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import datetime, socket

from app.db.session import get_session

router = APIRouter(prefix="", tags=["monitoring"])


@router.get("/healthz2")
def healthz() -> dict[str, str]:
    """
    Health check básico da aplicação.
    - Apenas retorna status `ok`.
    """
    return {"status": "ok"}


@router.get("/readyz")
def readyz(db: Session = Depends(get_session)) -> dict[str, str]:
    """
    Readiness check da aplicação.

    Verifica:
    - Se a API está rodando
    - Se o banco de dados responde
    - Hostname e timestamp (útil em clusters)
    """
    health = {
        "app_status": "ok",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "hostname": socket.gethostname(),
    }

    try:
        db.execute("SELECT 1")
        health["database"] = "connected"
    except Exception as e:
        health["database"] = f"error: {str(e)}"

    return health
