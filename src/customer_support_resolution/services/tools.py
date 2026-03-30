"""Tool gateway skeleton."""

from __future__ import annotations

from customer_support_resolution.connectors.crm import CRMConnector
from customer_support_resolution.domain.models import AccountContext, CRMAccountLookup, TicketPayload


class ToolGateway:
    """Native tool access layer for workflow investigation."""

    def __init__(self, crm_connector: CRMConnector | None = None) -> None:
        self.crm_connector = crm_connector or CRMConnector()

    def summarize_available_tools(self, account_context: AccountContext, ticket: TicketPayload) -> list[str]:
        tools = ["kb.search", "ticket.lookup"]
        if account_context.plan_type == "enterprise":
            tools.append("crm.lookup")
        if "refund" in ticket.body.lower() or "invoice" in ticket.body.lower():
            tools.append("billing.history")
        return tools

    def lookup_crm_account(self, account_id: str | None) -> CRMAccountLookup | None:
        if not account_id:
            return None
        try:
            return self.crm_connector.lookup_account_with_source(account_id)
        except KeyError:
            return None
