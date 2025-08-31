# app/core/errors.py
from __future__ import annotations

import logging
import os
import re
from http import HTTPStatus
from typing import Any, Dict, List, Optional, TypedDict

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger("ppghub.errors")

# ------------------------------------------------------------
# Config
# ------------------------------------------------------------
DEBUG: bool = os.getenv("PPGHUB_DEBUG", "false").lower() in {"1", "true", "yes"}

# ------------------------------------------------------------
# RFC 7807 schema
# ------------------------------------------------------------
class ProblemDetails(BaseModel):
    """RFC 7807 - application/problem+json.

    Campos padronizados. `errors` e `meta` são extensões (permitidas pelo RFC).
    """
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
    errors: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

def _status_title(code: int) -> str:
    """Retorna a frase padrão do status HTTP (ex.: 404 -> 'Not Found')."""
    try:
        return HTTPStatus(code).phrase
    except ValueError:
        return "HTTP Error"

def _problem_response(pd: ProblemDetails) -> JSONResponse:
    """Gera JSONResponse com o media type correto para Problem+JSON."""
    return JSONResponse(
        status_code=pd.status,
        content=pd.model_dump(exclude_none=True),
        media_type="application/problem+json",
    )

# ------------------------------------------------------------
# Helpers de construção de Problem Details
# ------------------------------------------------------------
def build_problem(
    *,
    request: Request,
    status_code: int,
    title: str | None = None,
    detail: str | None = None,
    type_url: str | None = None,
    errors: Dict[str, Any] | None = None,
    meta: Dict[str, Any] | None = None,
) -> ProblemDetails:
    """Factory para montar ProblemDetails consistente."""
    return ProblemDetails(
        type=type_url or "about:blank",
        title=title or _status_title(status_code),
        status=status_code,
        detail=detail,
        instance=str(request.url),
        errors=errors,
        meta={"method": request.method, **(meta or {})},
    )

# ------------------------------------------------------------
# Exception Handlers
# ------------------------------------------------------------
def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Trata HTTPException (ex.: 404/401/403) em Problem+JSON."""
    # `exc.detail` pode ser str ou dict; use como detail quando for str.
    detail = exc.detail if isinstance(exc.detail, str) else None
    logger.warning("HTTPException %s: %s %s", exc.status_code, request.method, request.url)
    pd = build_problem(
        request=request,
        status_code=exc.status_code,
        detail=detail,
        # `type` opcionalmente poderia apontar para uma doc (ex.: /errors/404)
    )
    return _problem_response(pd)

def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """422 de validação Pydantic/FastAPI."""
    logger.warning("Validation error: %s %s | %s", request.method, request.url, exc.errors())
    items: List[Dict[str, Any]] = [
        {"loc": e.get("loc"), "msg": e.get("msg"), "type": e.get("type")}
        for e in exc.errors()
    ]
    pd = build_problem(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        title="Unprocessable Entity",
        detail="Erros de validação no corpo/parâmetros.",
        type_url="urn:ppghub:errors:validation",
        errors={"items": items},
    )
    return _problem_response(pd)

# Regex para extrair campo/valor do erro de unicidade (psycopg2)
_UNIQUE = re.compile(r"Key \((?P<field>\w+)\)=\((?P<value>.+?)\) already exists")

def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """409 para violações de integridade (ex.: unique_violation 23505 no Postgres)."""
    # Evite vazar muita informação; log completo, resposta resumida.
    orig = getattr(exc, "orig", None)
    pgcode = getattr(orig, "pgcode", None)  # psycopg2: 23505 = unique_violation
    msg = str(orig) if orig is not None else str(exc)

    hint: Dict[str, Any] | None = None
    if m := _UNIQUE.search(msg):
        hint = {"field": m.group("field"), "value": m.group("value")}

    logger.error("IntegrityError (%s): %s %s | %s", pgcode, request.method, request.url, msg)

    pd = build_problem(
        request=request,
        status_code=status.HTTP_409_CONFLICT,
        title="Conflict",
        detail="Conflito com restrições do banco de dados.",
        type_url="urn:ppghub:errors:conflict",
        errors={"db_code": pgcode, "hint": hint},
    )
    return _problem_response(pd)

def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """500 genérico: não vaza detalhes em produção."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url, exc_info=exc)

    # Em DEBUG podemos expor `detail` (útil no dev); em produção, mensagem neutra.
    detail = str(exc) if DEBUG else "Ocorreu um erro interno no servidor."
    pd = build_problem(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        title="Internal Server Error",
        detail=detail,
        type_url="urn:ppghub:errors:internal",
        meta={"request_id": request.headers.get("x-request-id")},
    )
    return _problem_response(pd)
