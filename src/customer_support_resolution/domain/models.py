"""Core domain models for the customer support resolution skeleton."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Priority(str, Enum):
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketStatus(str, Enum):
    ACCEPTED = "accepted"
    TRIAGING = "triaging"
    APPROVAL_PENDING = "approval_pending"
    COMPLETED = "completed"


class AttachmentRef(BaseModel):
    type: str
    name: str
    content_ref: str


class Requester(BaseModel):
    id: str
    email: str
    name: str | None = None


class AccountContext(BaseModel):
    account_id: str
    org_id: str | None = None
    plan_type: str | None = None
    product: str | None = None
    product_version: str | None = None


class TicketPayload(BaseModel):
    title: str
    body: str
    attachments: list[AttachmentRef] = Field(default_factory=list)


class IntakeRequest(BaseModel):
    tenant_id: str
    source: str
    external_ticket_id: str
    requester: Requester
    account_context: AccountContext
    ticket: TicketPayload
    metadata: dict[str, Any] = Field(default_factory=dict)


class TriageResult(BaseModel):
    category: str
    priority: Priority
    risk_level: RiskLevel
    selected_skills: list[str] = Field(default_factory=list)


class Evidence(BaseModel):
    source_name: str
    source_ref: str
    content: str
    confidence: float = 0.0


class CRMAccountSnapshot(BaseModel):
    account_id: str
    org_name: str
    plan_type: str
    health_status: str
    open_incident_count: int
    last_ticket_id: str


class CRMAccountLookup(BaseModel):
    snapshot: CRMAccountSnapshot
    source: str


class Resolution(BaseModel):
    diagnosis_summary: str
    confidence: float
    recommended_action: str
    user_reply: str
    internal_notes: str


class RunSummary(BaseModel):
    run_id: str
    trace_id: str
    workflow_status: TicketStatus
    approval_required: bool
    triage: TriageResult
    evidence: list[Evidence] = Field(default_factory=list)
    resolution: Resolution
    created_at: datetime


def make_run_id() -> str:
    return f"run_{uuid4().hex[:12]}"


def make_trace_id() -> str:
    return f"trace_{uuid4().hex[:12]}"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
