"""Retrieval service skeleton."""

from __future__ import annotations

from customer_support_resolution.domain.models import AccountContext, Evidence, TicketPayload


class RetrievalService:
    """Returns minimal evidence scaffolding for the current request."""

    def collect(self, ticket: TicketPayload, account_context: AccountContext) -> list[Evidence]:
        source = account_context.product or "knowledge-base"
        return [
            Evidence(
                source_name=source,
                source_ref="kb://support/default",
                content=f"Initial evidence bundle for ticket: {ticket.title}",
                confidence=0.55,
            )
        ]
