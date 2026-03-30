from customer_support_resolution.mcp.server import MinimalMCPServer


def test_mcp_server_initialize_returns_protocol_version():
    server = MinimalMCPServer()

    response = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        }
    )

    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert response["result"]["protocolVersion"] == "2024-11-05"


def test_mcp_server_lists_crm_lookup_tool():
    server = MinimalMCPServer()

    response = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
        }
    )

    tools = response["result"]["tools"]

    assert len(tools) == 1
    assert tools[0]["name"] == "crm_lookup"
    assert "account_id" in tools[0]["inputSchema"]["properties"]


def test_mcp_server_calls_crm_lookup_tool():
    server = MinimalMCPServer()

    response = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "crm_lookup",
                "arguments": {
                    "account_id": "acc_1",
                },
            },
        }
    )

    content = response["result"]["content"]

    assert len(content) == 1
    assert content[0]["type"] == "text"
    assert "Acme Corp" in content[0]["text"]
    assert "at_risk" in content[0]["text"]
