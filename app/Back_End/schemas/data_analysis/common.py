"""Shared schema building blocks."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


T = TypeVar("T")


class ORMModel(BaseModel):
    """Base for schemas that read from ORM models via `from_attributes`."""

    model_config = ConfigDict(from_attributes=True)


class Page(BaseModel, Generic[T]):
    """Generic pagination wrapper."""

    items: list[T]
    total: int
    limit: int
    offset: int


class ErrorDetail(BaseModel):
    """Standard error envelope returned on any non-2xx response."""

    code: str
    message: str
    details: dict | None = None
