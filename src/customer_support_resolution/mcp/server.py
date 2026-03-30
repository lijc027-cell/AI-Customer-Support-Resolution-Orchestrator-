"""Minimal MCP-compatible server exposing CRM lookup over stdio."""

from __future__ import annotations

import json
import sys
from typing import Any

from customer_support_resolution.connectors.crm import CRMConnector


class MinimalMCPServer:
    """Small JSON-RPC style MCP server for local demonstrations."""

    def __init__(self, crm_connector: CRMConnector | None = None) -> None:
        self.crm_connector = crm_connector or CRMConnector()

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        method = request.get("method")
        request_id = request.get("id")

        if method == "initialize":
            return self._success(
                request_id,
                {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "customer-support-resolution-mcp",
                        "version": "0.1.0",
                    },
                    "capabilities": {
                        "tools": {},
                    },
                },
            )

        if method == "tools/list":
            return self._success(request_id, {"tools": [self._crm_lookup_definition()]})

        if method == "tools/call":
            return self._handle_tool_call(request_id, request.get("params", {}))

        return self._error(request_id, -32601, f"Method not found: {method}")

    def serve_forever(self) -> None:
        for line in sys.stdin:
            payload = line.strip()
            if not payload:
                continue
            response = self.handle_request(json.loads(payload))
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

    def _handle_tool_call(self, request_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        if params.get("name") != "crm_lookup":
            return self._error(request_id, -32601, "Unknown tool")

        account_id = params.get("arguments", {}).get("account_id")
        if not account_id:
            return self._error(request_id, -32602, "Missing required argument: account_id")

        try:
            lookup = self.crm_connector.lookup_account_with_source(account_id)
        except KeyError as error:
            return self._error(request_id, -32004, str(error))
        except PermissionError as error:
            return self._error(request_id, -32001, str(error))

        snapshot = lookup.snapshot
        text = (
            f"Account {snapshot.org_name} ({snapshot.account_id}) "
            f"plan={snapshot.plan_type} health={snapshot.health_status} "
            f"open_incidents={snapshot.open_incident_count} last_ticket={snapshot.last_ticket_id} "
            f"retrieval_source={lookup.source}"
        )
        return self._success(
            request_id,
            {
                "content": [
                    {
                        "type": "text",
                        "text": text,
                    }
                ]
            },
        )

    def _crm_lookup_definition(self) -> dict[str, Any]:
        return {
            "name": "crm_lookup",
            "description": "Look up CRM context for an account_id.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Internal account identifier.",
                    }
                },
                "required": ["account_id"],
            },
        }

    def _success(self, request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }

    def _error(self, request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message,
            },
        }


def main() -> None:
    MinimalMCPServer().serve_forever()


if __name__ == "__main__":
    main()
