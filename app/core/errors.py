# app/core/errors.py
from __future__ import annotations
from typing import Any, Dict, List
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
import re

"""
    Payload de erro no padrão RFC 7807.
    - type: URL (ou "about:blank") que identifica o tipo de problema.
    - title: título curto legível (ex.: "Violação de integridade").
    - status: HTTP status code (int).
    - detail: descrição mais específica do erro.
    - instance: URI da requisição (preenchido com request.url).
    - errors/meta: detalhes extras (ex.: lista de validação, hints de DB, method, request_id).
    """

class ProblemDetails(BaseModel):
    """Payload de erro no padrão RFC 7807 (Problem Details)."""
    type: str
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    errors: Dict[str, Any] | None = None
    meta: Dict[str, Any] | None = None

def _resp(pd: ProblemDetails) -> JSONResponse:
    return JSONResponse(pd.model_dump(exclude_none=True), status_code=pd.status)

def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    pd = ProblemDetails(
        type="about:blank",
        title=str(exc.detail) if exc.detail else "HTTP error",
        status=exc.status_code,
        detail=str(exc.detail) if exc.detail else None,
        instance=str(request.url),
        meta={"method": request.method},
    )
    return _resp(pd)

def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    items: List[Dict[str, Any]] = []
    for e in exc.errors():
        items.append({
            "loc": e.get("loc"),
            "msg": e.get("msg"),
            "type": e.get("type"),
        })
    pd = ProblemDetails(
        type="https://http.dev/validation-error",
        title="Payload inválido",
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Erros de validação no corpo/parâmetros.",
        instance=str(request.url),
        errors={"items": items},
        meta={"method": request.method},
    )
    return _resp(pd)

_UNIQUE = re.compile(r"Key \((?P<field>\w+)\)=\((?P<value>.+?)\) already exists")

def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    msg = str(exc.orig)
    hint = None
    if m := _UNIQUE.search(msg):
        hint = {"field": m.group("field"), "value": m.group("value")}
    pd = ProblemDetails(
        type="https://http.dev/conflict",
        title="Violação de integridade",
        status=status.HTTP_409_CONFLICT,
        detail="Conflito com restrições do banco (provável unicidade).",
        instance=str(request.url),
        errors={"db_error": msg, "hint": hint},
        meta={"method": request.method},
    )
    return _resp(pd)

def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    pd = ProblemDetails(
        type="https://http.dev/internal-error",
        title="Erro interno",
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Ocorreu um erro inesperado. Consulte os logs.",
        instance=str(request.url),
        meta={"method": request.method, "request_id": request.headers.get("x-request-id")},
    )
    return _resp(pd)
