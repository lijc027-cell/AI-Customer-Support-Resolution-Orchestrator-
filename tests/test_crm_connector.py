import json
from urllib.error import HTTPError

import pytest

from customer_support_resolution.connectors.crm import CRMConnector, HttpCRMTransport
from customer_support_resolution.services.tools import ToolGateway


class RecordingTransport:
    def __init__(self, payload: dict | None = None) -> None:
        self.payload = payload or {
            "account_id": "acc_1",
            "org_name": "Acme Corp",
            "plan_type": "enterprise",
            "health_status": "at_risk",
            "open_incident_count": 2,
            "last_ticket_id": "zd_0991",
        }
        self.calls: list[tuple[str, float]] = []

    def fetch_account(self, account_id: str, timeout_seconds: float) -> dict:
        self.calls.append((account_id, timeout_seconds))
        return self.payload


class FlakyTransport:
    def __init__(self, failures: int, payload: dict | None = None) -> None:
        self.failures = failures
        self.payload = payload or {
            "account_id": "acc_1",
            "org_name": "Acme Corp",
            "plan_type": "enterprise",
            "health_status": "at_risk",
            "open_incident_count": 2,
            "last_ticket_id": "zd_0991",
        }
        self.calls = 0

    def fetch_account(self, account_id: str, timeout_seconds: float) -> dict:
        self.calls += 1
        if self.calls <= self.failures:
            raise TimeoutError(f"timeout for {account_id}")
        return self.payload


class FakeHTTPResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self) -> "FakeHTTPResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class RecordingHTTPOpener:
    def __init__(self, payload: dict | None = None) -> None:
        self.payload = payload or {
            "account_id": "acc_1",
            "org_name": "Acme Corp",
            "plan_type": "enterprise",
            "health_status": "at_risk",
            "open_incident_count": 2,
            "last_ticket_id": "zd_0991",
        }
        self.calls: list[tuple[object, float]] = []

    def __call__(self, request: object, timeout: float) -> FakeHTTPResponse:
        self.calls.append((request, timeout))
        return FakeHTTPResponse(self.payload)


class UnauthorizedHTTPOpener:
    def __call__(self, request: object, timeout: float) -> FakeHTTPResponse:
        raise HTTPError(
            url=request.full_url,
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=None,
        )


def test_crm_connector_returns_account_snapshot():
    snapshot = CRMConnector().lookup_account("acc_1")

    assert snapshot.account_id == "acc_1"
    assert snapshot.org_name == "Acme Corp"
    assert snapshot.plan_type == "enterprise"
    assert snapshot.health_status == "at_risk"
    assert snapshot.open_incident_count == 2
    assert snapshot.last_ticket_id == "zd_0991"


def test_crm_connector_passes_timeout_to_transport():
    transport = RecordingTransport()
    connector = CRMConnector(transport=transport, request_timeout_seconds=2.5)

    snapshot = connector.lookup_account("acc_1")

    assert snapshot.account_id == "acc_1"
    assert transport.calls == [("acc_1", 2.5)]


def test_crm_connector_retries_after_timeout():
    transport = FlakyTransport(failures=1)
    connector = CRMConnector(
        transport=transport,
        request_timeout_seconds=1.0,
        max_retries=2,
    )

    snapshot = connector.lookup_account("acc_1")

    assert snapshot.account_id == "acc_1"
    assert transport.calls == 2


def test_crm_connector_falls_back_after_retry_exhaustion():
    transport = FlakyTransport(failures=3)
    connector = CRMConnector(
        transport=transport,
        request_timeout_seconds=1.0,
        max_retries=2,
    )

    snapshot = connector.lookup_account("acc_1")

    assert snapshot.account_id == "acc_1"
    assert snapshot.org_name == "Acme Corp"
    assert transport.calls == 3


def test_crm_connector_raises_when_remote_and_fallback_are_missing():
    transport = FlakyTransport(
        failures=3,
        payload={
            "account_id": "acc_missing",
            "org_name": "Missing Co",
            "plan_type": "business",
            "health_status": "healthy",
            "open_incident_count": 0,
            "last_ticket_id": "zd_0000",
        },
    )
    connector = CRMConnector(
        transport=transport,
        fallback_accounts={},
        max_retries=1,
    )

    with pytest.raises(TimeoutError):
        connector.lookup_account("acc_missing")


def test_http_crm_transport_fetches_json_payload():
    opener = RecordingHTTPOpener()
    transport = HttpCRMTransport(
        base_url="https://crm.internal/api",
        opener=opener,
    )

    payload = transport.fetch_account("acc_1", timeout_seconds=3.0)

    assert payload["account_id"] == "acc_1"
    request, timeout = opener.calls[0]
    assert request.full_url == "https://crm.internal/api/accounts/acc_1"
    assert timeout == 3.0


def test_http_crm_transport_adds_bearer_token_header():
    opener = RecordingHTTPOpener()
    transport = HttpCRMTransport(
        base_url="https://crm.internal/api",
        api_token="secret-token",
        opener=opener,
    )

    transport.fetch_account("acc_1", timeout_seconds=3.0)

    request, _ = opener.calls[0]

    assert request.get_header("Authorization") == "Bearer secret-token"


def test_http_crm_transport_raises_permission_error_for_unauthorized():
    transport = HttpCRMTransport(
        base_url="https://crm.internal/api",
        opener=UnauthorizedHTTPOpener(),
    )

    with pytest.raises(PermissionError):
        transport.fetch_account("acc_1", timeout_seconds=1.0)


def test_tool_gateway_exposes_fallback_lookup_source():
    transport = FlakyTransport(failures=3)
    connector = CRMConnector(
        transport=transport,
        request_timeout_seconds=1.0,
        max_retries=2,
    )

    lookup = ToolGateway(crm_connector=connector).lookup_crm_account("acc_1")

    assert lookup is not None
    assert lookup.source == "fallback"
    assert lookup.snapshot.account_id == "acc_1"
