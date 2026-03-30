"""Public API response models."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

from customer_support_resolution.domain.models import RunSummary

T = TypeVar("T")


class ErrorPayload(BaseModel):
    code: str
    message: str


class ApiResponse(BaseModel, Generic[T]):
    request_id: str
    data: T | None
    error: ErrorPayload | None = None


class HealthResponse(BaseModel):
    service: str
    status: str


class IntakeAcceptedResponse(BaseModel):
    ticket_id: str
    run: RunSummary
