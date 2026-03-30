"""Trace service skeleton."""

from __future__ import annotations

from customer_support_resolution.domain.models import RunSummary


class TraceService:
    """Creates a minimal trace timeline representation."""

    def snapshot(self, run: RunSummary) -> dict[str, object]:
        return {
            "trace_id": run.trace_id,
            "timeline": [
                {"node": "triage", "status": "completed"},
                {"node": "investigator", "status": "completed"},
                {"node": "resolver", "status": "completed"},
                {"node": "verifier", "status": "completed"},
            ],
        }
