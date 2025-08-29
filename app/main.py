from __future__ import annotations
import datetime, socket
import time
from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from app.api.routes import programas
from app.api.routes.instituicoes import router as instituicoes_router
from app.api.routes.roles import router as roles_router
from app.api.routes.usuarios import router as usuarios_router
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.deps import get_session, get_db
from app.db.session import init_db
import socket
from sqlalchemy import text
from app.core.errors import (
    http_exception_handler,
    validation_exception_handler,
    integrity_error_handler,
    unhandled_exception_handler,
)
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title="PPGHUB API", version="0.1.0")

# “Nada silencioso”: handlers globais
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)



# ----------------- REGISTRO DE ROTAS -----------------
app.include_router(instituicoes_router)
app.include_router(roles_router)
app.include_router(usuarios_router)
app.include_router(programas.router)

@app.on_event("startup")
def on_startup():
    init_db()

# rota raiz
@app.get("/")
async def root():
    return {"message": "Bem-vindo à API do PPG Hub!"}

@app.get("/healthzzzz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/ping")
def ping():
    return {"pong": True}


@app.get("/routers-ping", tags=["monitoring"])
def routers_ping() -> dict:
    """
    Lista todas as rotas registradas no FastAPI.
    Útil para verificar se os routers foram incluídos corretamente.
    """
    routers_info = []
    for route in app.routes:
        if hasattr(route, "methods"):
            routers_info.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name,
            })

    return {
        "total_routes": len(routers_info),
        "routers": routers_info
    }



@app.get("/testdb")
def test_db(db: Session = Depends(get_db)):
    return {"ok": str(db.execute("SELECT 1").scalar())}
@app.get("/hp", tags=["monitoring"])
def health_plus(db: Session = Depends(get_session)) -> dict:
    """
    Health check avançado:
    - Status da aplicação
    - Conexão e tempo de resposta do banco
    - Schemas disponíveis
    - Ambiente e versão da aplicação
    """
    health = {
        "app_status": "ok",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "hostname": socket.gethostname(),
        "environment": settings.ENVIRONMENT,
        "database": {},
    }

    # Testa conexão com o banco e mede latência
    try:
        start = time.perf_counter()
        db.execute(text("SELECT 1"))
        latency = (time.perf_counter() - start) * 1000  # ms
        health["database"]["status"] = "connected"
        health["database"]["latency_ms"] = round(latency, 2)

        # Lista schemas disponíveis
        result = db.execute(
            text("SELECT schema_name FROM information_schema.schemata;")
        )
        schemas = [row[0] for row in result]
        health["database"]["schemas"] = schemas

        # Valida se os schemas críticos existem
        required = {"auth", "core", "academic"}
        missing = list(required - set(schemas))
        health["database"]["required_schemas_ok"] = not missing
        if missing:
            health["database"]["missing_schemas"] = missing

    except Exception as e:
        health["database"]["status"] = "error"
        health["database"]["detail"] = str(e)

    return health

