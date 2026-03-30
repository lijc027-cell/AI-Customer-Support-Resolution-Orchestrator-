"""Approval service skeleton."""

from __future__ import annotations


class ApprovalService:
    """Generates an approval hint without persistence."""

    def describe_requirement(self, approval_required: bool) -> str:
        if approval_required:
            return "Manual approval required before automated action."
        return "No approval required."
