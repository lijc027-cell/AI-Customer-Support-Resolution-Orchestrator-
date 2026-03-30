from customer_support_resolution.dependencies import build_crm_connector
from customer_support_resolution.domain.models import IntakeRequest
from customer_support_resolution.mock_services.crm_api import run_mock_crm_server
from customer_support_resolution.services.tools import ToolGateway
from customer_support_resolution.services.workflow import CustomerSupportWorkflow
from customer_support_resolution.settings import AppSettings


def make_http_intake_payload() -> dict:
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
            "account_id": "acc_remote",
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


def test_workflow_fetches_crm_evidence_from_http_service():
    accounts = {
        "acc_remote": {
            "account_id": "acc_remote",
            "org_name": "Remote Labs",
            "plan_type": "enterprise",
            "health_status": "escalated",
            "open_incident_count": 4,
            "last_ticket_id": "zd_2007",
        }
    }
    payload = make_http_intake_payload()

    with run_mock_crm_server(accounts) as base_url:
        settings = AppSettings(
            crm_transport="http",
            crm_base_url=base_url,
        )
        connector = build_crm_connector(settings)
        workflow = CustomerSupportWorkflow(tools=ToolGateway(crm_connector=connector))

        run = workflow.run(IntakeRequest.model_validate(payload))

    crm_evidence = next(item for item in run.evidence if item.source_name == "crm")

    assert crm_evidence.source_ref == "crm://accounts/acc_remote"
    assert "Remote Labs" in crm_evidence.content
    assert "escalated" in crm_evidence.content
    assert "retrieval_source=remote" in crm_evidence.content


def test_workflow_fetches_crm_evidence_from_authorized_http_service():
    accounts = {
        "acc_remote": {
            "account_id": "acc_remote",
            "org_name": "Remote Labs",
            "plan_type": "enterprise",
            "health_status": "escalated",
            "open_incident_count": 4,
            "last_ticket_id": "zd_2007",
        }
    }
    payload = make_http_intake_payload()

    with run_mock_crm_server(accounts, required_token="valid-token") as base_url:
        settings = AppSettings(
            crm_transport="http",
            crm_base_url=base_url,
            crm_api_token="valid-token",
        )
        connector = build_crm_connector(settings)
        workflow = CustomerSupportWorkflow(tools=ToolGateway(crm_connector=connector))
        run = workflow.run(IntakeRequest.model_validate(payload))

    crm_evidence = next(item for item in run.evidence if item.source_name == "crm")

    assert "Remote Labs" in crm_evidence.content
    assert "retrieval_source=remote" in crm_evidence.content


def test_workflow_raises_for_unauthorized_http_crm_access():
    accounts = {
        "acc_remote": {
            "account_id": "acc_remote",
            "org_name": "Remote Labs",
            "plan_type": "enterprise",
            "health_status": "escalated",
            "open_incident_count": 4,
            "last_ticket_id": "zd_2007",
        }
    }
    payload = make_http_intake_payload()

    with run_mock_crm_server(accounts, required_token="valid-token") as base_url:
        settings = AppSettings(
            crm_transport="http",
            crm_base_url=base_url,
        )
        connector = build_crm_connector(settings)
        workflow = CustomerSupportWorkflow(tools=ToolGateway(crm_connector=connector))

        try:
            workflow.run(IntakeRequest.model_validate(payload))
            raised = None
        except PermissionError as error:
            raised = error

    assert raised is not None
