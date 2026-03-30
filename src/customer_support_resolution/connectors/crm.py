"""CRM connector with transport abstraction, retries, and local fallback."""

from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.request import Request
from typing import Protocol
from urllib.request import urlopen

from customer_support_resolution.domain.models import CRMAccountLookup, CRMAccountSnapshot


DEFAULT_CRM_ACCOUNTS = {
    "acc_1": CRMAccountSnapshot(
        account_id="acc_1",
        org_name="Acme Corp",
        plan_type="enterprise",
        health_status="at_risk",
        open_incident_count=2,
        last_ticket_id="zd_0991",
    ),
    "acc_2": CRMAccountSnapshot(
        account_id="acc_2",
        org_name="Northwind Health",
        plan_type="business",
        health_status="healthy",
        open_incident_count=0,
        last_ticket_id="zd_0874",
    ),
}


class CRMTransport(Protocol):
    def fetch_account(self, account_id: str, timeout_seconds: float) -> dict:
        ...


class FixtureCRMTransport:
    def __init__(self, accounts: dict[str, CRMAccountSnapshot] | None = None) -> None:
        self.accounts = accounts or DEFAULT_CRM_ACCOUNTS

    def fetch_account(self, account_id: str, timeout_seconds: float) -> dict:
        snapshot = self.accounts.get(account_id)
        if snapshot is None:
            raise KeyError(f"CRM account not found: {account_id}")
        return snapshot.model_dump()


class HttpCRMTransport:
    def __init__(self, base_url: str, api_token: str | None = None, opener=urlopen) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.opener = opener

    def fetch_account(self, account_id: str, timeout_seconds: float) -> dict:
        request = Request(f"{self.base_url}/accounts/{account_id}")
        if self.api_token:
            request.add_header("Authorization", f"Bearer {self.api_token}")

        try:
            with self.opener(request, timeout=timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            if error.code == 404:
                raise KeyError(f"CRM account not found: {account_id}") from error
            if error.code in {401, 403}:
                raise PermissionError("CRM authorization failed") from error
            if error.code in {429, 500, 502, 503, 504}:
                raise ConnectionError(f"CRM upstream unavailable: {error.code}") from error
            raise OSError(f"CRM request failed: {error.code}") from error


class CRMConnector:
    """CRM connector that isolates retry and fallback behavior."""

    def __init__(
        self,
        transport: CRMTransport | None = None,
        fallback_accounts: dict[str, CRMAccountSnapshot] | None = None,
        request_timeout_seconds: float = 1.5,
        max_retries: int = 2,
    ) -> None:
        self.fallback_accounts = fallback_accounts if fallback_accounts is not None else DEFAULT_CRM_ACCOUNTS
        self.transport = transport or FixtureCRMTransport(self.fallback_accounts)
        self.request_timeout_seconds = request_timeout_seconds
        self.max_retries = max_retries

    def lookup_account(self, account_id: str) -> CRMAccountSnapshot:
        return self.lookup_account_with_source(account_id).snapshot

    def lookup_account_with_source(self, account_id: str) -> CRMAccountLookup:
        last_error: Exception | None = None

        for _ in range(self.max_retries + 1):
            try:
                payload = self.transport.fetch_account(account_id, self.request_timeout_seconds)
                return CRMAccountLookup(
                    snapshot=CRMAccountSnapshot.model_validate(payload),
                    source="remote",
                )
            except KeyError:
                break
            except PermissionError:
                raise
            except (TimeoutError, ConnectionError, OSError) as error:
                last_error = error

        fallback = self.fallback_accounts.get(account_id)
        if fallback is not None:
            return CRMAccountLookup(snapshot=fallback, source="fallback")
        if last_error is not None:
            raise last_error
        raise KeyError(f"CRM account not found: {account_id}")
