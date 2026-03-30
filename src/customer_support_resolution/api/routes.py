"""API routes for the customer support resolution skeleton."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from customer_support_resolution.dependencies import get_workflow
from customer_support_resolution.domain.models import IntakeRequest
from customer_support_resolution.schemas.api import ApiResponse, HealthResponse, IntakeAcceptedResponse
from customer_support_resolution.services.workflow import CustomerSupportWorkflow

router = APIRouter()


@router.get("/health")
def health() -> ApiResponse[HealthResponse]:
    return ApiResponse(
        request_id=f"req_{uuid4().hex[:12]}",
        data=HealthResponse(service="customer-support-resolution", status="ok"),
    )


@router.post("/tickets/intake")
def intake_ticket(
    payload: IntakeRequest,
    workflow: CustomerSupportWorkflow = Depends(get_workflow),
) -> ApiResponse[IntakeAcceptedResponse]:
    run = workflow.run(payload)
    return ApiResponse(
        request_id=f"req_{uuid4().hex[:12]}",
        data=IntakeAcceptedResponse(
            ticket_id=payload.external_ticket_id,
            run=run,
        ),
    )


@router.get("/runs/{run_id}")
def get_run(
    run_id: str,
    workflow: CustomerSupportWorkflow = Depends(get_workflow),
) -> ApiResponse[object]:
    run = workflow.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return ApiResponse(
        request_id=f"req_{uuid4().hex[:12]}",
        data=run,
    )
