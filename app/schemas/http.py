# app/schemas/http.py
from __future__ import annotations
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar("T")

class ProblemDetails(BaseModel):
    """RFC 7807: corpo padrão de erros."""
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None

class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int

class Page(BaseModel, Generic[T]):
    """Listas paginadas previsíveis no front."""
    data: List[T]
    meta: PageMeta
