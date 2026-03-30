"""Audit service skeleton."""

from __future__ import annotations

from customer_support_resolution.domain.models import IntakeRequest, RunSummary


class AuditService:
    """Produces a tiny audit summary for the run."""

    def record(self, intake: IntakeRequest, run: RunSummary) -> dict[str, str]:
        return {
            "tenant_id": intake.tenant_id,
            "external_ticket_id": intake.external_ticket_id,
            "run_id": run.run_id,
        }
