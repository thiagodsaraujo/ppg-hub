from __future__ import annotations
from fastapi import FastAPI
from app.api.routes.instituicoes import router as instituicoes_router

app = FastAPI(title="PPGHUB API")
app.include_router(instituicoes_router)

@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
