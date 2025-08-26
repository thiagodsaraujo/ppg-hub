from __future__ import annotations
import datetime, socket
from fastapi import FastAPI
from app.api.routes.instituicoes import router as instituicoes_router
from app.api.routes.roles import router as roles_router
from sqlalchemy.orm import Session
from fastapi import Depends
from app.api.routes.monitoring import router as monitoring_router  # 👈 novo
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_session
import socket


app = FastAPI(title="PPGHUB API")

# inclui routers
app.include_router(instituicoes_router)
app.include_router(roles_router)
app.include_router(monitoring_router)



@app.get("/healthzzzz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/hp", tags=["monitoring"])
def health_plus(db: Session = Depends(get_session)) -> dict[str, str]:
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

