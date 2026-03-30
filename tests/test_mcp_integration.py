from customer_support_resolution.dependencies import build_mcp_server
from customer_support_resolution.mock_services.crm_api import run_mock_crm_server
from customer_support_resolution.settings import AppSettings


def test_mcp_server_fetches_crm_data_from_http_service():
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

    with run_mock_crm_server(accounts) as base_url:
        server = build_mcp_server(
            AppSettings(
                crm_transport="http",
                crm_base_url=base_url,
            )
        )
        response = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {
                    "name": "crm_lookup",
                    "arguments": {
                        "account_id": "acc_remote",
                    },
                },
            }
        )

    content = response["result"]["content"]

    assert len(content) == 1
    assert "Remote Labs" in content[0]["text"]
    assert "escalated" in content[0]["text"]
    assert "retrieval_source=remote" in content[0]["text"]


def test_mcp_server_fetches_crm_data_from_authorized_http_service():
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

    with run_mock_crm_server(accounts, required_token="valid-token") as base_url:
        server = build_mcp_server(
            AppSettings(
                crm_transport="http",
                crm_base_url=base_url,
                crm_api_token="valid-token",
            )
        )
        response = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 9,
                "method": "tools/call",
                "params": {
                    "name": "crm_lookup",
                    "arguments": {
                        "account_id": "acc_remote",
                    },
                },
            }
        )

    assert "Remote Labs" in response["result"]["content"][0]["text"]


def test_mcp_server_returns_auth_error_for_unauthorized_http_crm_access():
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

    with run_mock_crm_server(accounts, required_token="valid-token") as base_url:
        server = build_mcp_server(
            AppSettings(
                crm_transport="http",
                crm_base_url=base_url,
            )
        )
        response = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 8,
                "method": "tools/call",
                "params": {
                    "name": "crm_lookup",
                    "arguments": {
                        "account_id": "acc_remote",
                    },
                },
            }
        )

    assert response["error"]["code"] == -32001
