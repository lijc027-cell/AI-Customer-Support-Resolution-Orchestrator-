"""Workflow orchestration skeleton for the customer support project."""

from __future__ import annotations

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from customer_support_resolution.domain.models import (
    Evidence,
    IntakeRequest,
    Priority,
    Resolution,
    RiskLevel,
    RunSummary,
    TicketStatus,
    TriageResult,
    make_run_id,
    make_trace_id,
    utc_now,
)
from customer_support_resolution.services.approval import ApprovalService
from customer_support_resolution.services.audit import AuditService
from customer_support_resolution.services.policy import PolicyEngine
from customer_support_resolution.services.retrieval import RetrievalService
from customer_support_resolution.services.run_store import RunStore
from customer_support_resolution.services.skills import SkillRegistry
from customer_support_resolution.services.tools import ToolGateway
from customer_support_resolution.services.trace import TraceService


class WorkflowState(TypedDict):
    intake: IntakeRequest
    triage: TriageResult
    evidence: list[Evidence]
    available_tools: list[str]
    resolution: Resolution
    approval_required: bool
    workflow_status: str


class CustomerSupportWorkflow:
    """A minimal, deterministic workflow that mirrors the planned system shape."""

    def __init__(
        self,
        retrieval: RetrievalService | None = None,
        tools: ToolGateway | None = None,
        skills: SkillRegistry | None = None,
        policy: PolicyEngine | None = None,
        approval: ApprovalService | None = None,
        audit: AuditService | None = None,
        trace: TraceService | None = None,
        store: RunStore | None = None,
    ) -> None:
        self.retrieval = retrieval or RetrievalService()
        self.tools = tools or ToolGateway()
        self.skills = skills or SkillRegistry()
        self.policy = policy or PolicyEngine()
        self.approval = approval or ApprovalService()
        self.audit = audit or AuditService()
        self.trace = trace or TraceService()
        self.store = store or RunStore()
        self.checkpointer = InMemorySaver()
        self.graph = self._build_graph()

    def run(self, intake: IntakeRequest) -> RunSummary:
        state = self.graph.invoke(
            {
                "intake": intake,
                "triage": self._empty_triage(),
                "evidence": [],
                "available_tools": [],
                "resolution": self._empty_resolution(),
                "approval_required": False,
                "workflow_status": TicketStatus.TRIAGING.value,
            },
            config={"configurable": {"thread_id": make_trace_id()}},
        )
        triage = state["triage"]
        evidence = state["evidence"]
        resolution = state["resolution"]
        approval_required = state["approval_required"]
        status = TicketStatus(state["workflow_status"])

        run = RunSummary(
            run_id=make_run_id(),
            trace_id=make_trace_id(),
            workflow_status=status,
            approval_required=approval_required,
            triage=triage,
            evidence=evidence,
            resolution=resolution,
            created_at=utc_now(),
        )
        self.audit.record(intake, run)
        self.trace.snapshot(run)
        self.store.save(
            run,
            {
                "workflow_status": state["workflow_status"],
                "approval_required": approval_required,
                "available_tools": state["available_tools"],
                "triage": triage.model_dump(mode="json"),
            },
        )
        return run

    def get_run(self, run_id: str) -> RunSummary | None:
        return self.store.load_run(run_id)

    def _build_graph(self):
        graph = StateGraph(WorkflowState)
        graph.add_node("triage", self._triage_node)
        graph.add_node("investigate", self._investigate_node)
        graph.add_node("resolve", self._resolve_node)
        graph.add_node("verify", self._verify_node)
        graph.add_edge(START, "triage")
        graph.add_edge("triage", "investigate")
        graph.add_edge("investigate", "resolve")
        graph.add_edge("resolve", "verify")
        graph.add_edge("verify", END)
        return graph.compile(checkpointer=self.checkpointer)

    def _triage_node(self, state: WorkflowState) -> dict[str, object]:
        return {"triage": self._triage(state["intake"])}

    def _investigate_node(self, state: WorkflowState) -> dict[str, object]:
        intake = state["intake"]
        evidence = self.retrieval.collect(intake.ticket, intake.account_context)
        crm_lookup = self.tools.lookup_crm_account(intake.account_context.account_id)
        if crm_lookup is not None:
            crm_snapshot = crm_lookup.snapshot
            evidence.append(
                Evidence(
                    source_name="crm",
                    source_ref=f"crm://accounts/{crm_snapshot.account_id}",
                    content=(
                        f"{crm_snapshot.org_name} is {crm_snapshot.health_status} with "
                        f"{crm_snapshot.open_incident_count} open incidents. "
                        f"Last related ticket: {crm_snapshot.last_ticket_id}. "
                        f"retrieval_source={crm_lookup.source}"
                    ),
                    confidence=0.91,
                )
            )
        return {
            "evidence": evidence,
            "available_tools": self.tools.summarize_available_tools(intake.account_context, intake.ticket),
        }

    def _resolve_node(self, state: WorkflowState) -> dict[str, object]:
        return {
            "resolution": self._resolve(
                state["intake"],
                state["triage"],
                state["available_tools"],
            )
        }

    def _verify_node(self, state: WorkflowState) -> dict[str, object]:
        approval_required = self.policy.requires_approval(state["triage"].risk_level)
        workflow_status = (
            TicketStatus.APPROVAL_PENDING.value if approval_required else TicketStatus.COMPLETED.value
        )
        return {
            "approval_required": approval_required,
            "workflow_status": workflow_status,
        }

    def _triage(self, intake: IntakeRequest) -> TriageResult:
        text = f"{intake.ticket.title}\n{intake.ticket.body}".lower()
        category = "general_support"
        priority = Priority.P2
        risk_level = RiskLevel.LOW

        if "refund" in text or "invoice" in text or "billing" in text:
            category = "billing"
            risk_level = RiskLevel.HIGH
        elif "sso" in text or "certificate" in text or "login" in text:
            category = "sso"
            risk_level = RiskLevel.MEDIUM

        if "urgent" in text or "outage" in text:
            priority = Priority.P1
            if risk_level == RiskLevel.LOW:
                risk_level = RiskLevel.MEDIUM

        selected_skills = self.skills.resolve(category, risk_level.value)
        return TriageResult(
            category=category,
            priority=priority,
            risk_level=risk_level,
            selected_skills=selected_skills,
        )

    def _resolve(self, intake: IntakeRequest, triage: TriageResult, available_tools: list[str]) -> Resolution:
        approval_note = self.approval.describe_requirement(
            triage.risk_level == RiskLevel.HIGH,
        )
        return Resolution(
            diagnosis_summary=f"Initial diagnosis for {triage.category} request.",
            confidence=0.72 if triage.risk_level != RiskLevel.HIGH else 0.64,
            recommended_action=f"Review evidence, then use tools: {', '.join(available_tools)}.",
            user_reply=(
                "We analyzed your request and prepared a support resolution draft. "
                "A support operator can continue from this workflow state."
            ),
            internal_notes=approval_note,
        )

    def _empty_triage(self) -> TriageResult:
        return TriageResult(
            category="unclassified",
            priority=Priority.P3,
            risk_level=RiskLevel.LOW,
            selected_skills=[],
        )

    def _empty_resolution(self) -> Resolution:
        return Resolution(
            diagnosis_summary="Not resolved yet.",
            confidence=0.0,
            recommended_action="No action yet.",
            user_reply="",
            internal_notes="",
        )
