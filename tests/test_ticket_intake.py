from fastapi.testclient import TestClient

from customer_support_resolution.domain.models import IntakeRequest
from customer_support_resolution.main import app
from customer_support_resolution.services.workflow import CustomerSupportWorkflow


def make_intake_payload() -> dict:
    return {
        "tenant_id": "tenant_acme",
        "source": "zendesk",
        "external_ticket_id": "zd_1001",
        "requester": {
            "id": "u_1",
            "email": "alice@acme.com",
            "name": "Alice",
        },
        "account_context": {
            "account_id": "acc_1",
            "org_id": "org_1",
            "plan_type": "enterprise",
            "product": "iam-cloud",
            "product_version": "v5.2.1",
        },
        "ticket": {
            "title": "Urgent refund issue",
            "body": "Need urgent billing refund investigation",
            "attachments": [],
        },
        "metadata": {
            "channel": "email",
        },
    }


def test_workflow_builds_langgraph_state_machine():
    workflow = CustomerSupportWorkflow()

    assert workflow.graph is not None


def test_ticket_intake_returns_run_summary():
    client = TestClient(app)

    response = client.post("/tickets/intake", json=make_intake_payload())

    assert response.status_code == 200
    payload = response.json()
    assert payload["error"] is None
    assert payload["data"]["ticket_id"] == "zd_1001"
    assert payload["data"]["run"]["triage"]["category"] == "billing"
    assert payload["data"]["run"]["approval_required"] is True


def test_ticket_run_can_be_loaded_after_persistence():
    client = TestClient(app)

    intake_response = client.post("/tickets/intake", json=make_intake_payload())

    run_id = intake_response.json()["data"]["run"]["run_id"]
    response = client.get(f"/runs/{run_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["error"] is None
    assert payload["data"]["run_id"] == run_id
    assert payload["data"]["triage"]["category"] == "billing"


def test_workflow_includes_crm_evidence_for_enterprise_account():
    workflow = CustomerSupportWorkflow()

    run = workflow.run(IntakeRequest.model_validate(make_intake_payload()))

    crm_evidence = next(item for item in run.evidence if item.source_name == "crm")

    assert crm_evidence.source_ref == "crm://accounts/acc_1"
    assert "Acme Corp" in crm_evidence.content
    assert "at_risk" in crm_evidence.content
