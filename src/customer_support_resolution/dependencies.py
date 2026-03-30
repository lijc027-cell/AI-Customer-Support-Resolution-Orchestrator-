"""Dependency builders for application services."""

from __future__ import annotations

from functools import lru_cache

from customer_support_resolution.connectors.crm import CRMConnector, FixtureCRMTransport, HttpCRMTransport
from customer_support_resolution.mcp.server import MinimalMCPServer
from customer_support_resolution.services.tools import ToolGateway
from customer_support_resolution.services.workflow import CustomerSupportWorkflow
from customer_support_resolution.settings import AppSettings


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings.from_env()


def build_crm_connector(settings: AppSettings) -> CRMConnector:
    transport = build_crm_transport(settings)
    return CRMConnector(
        transport=transport,
        request_timeout_seconds=settings.crm_timeout_seconds,
        max_retries=settings.crm_max_retries,
    )


def build_crm_transport(settings: AppSettings):
    if settings.crm_transport == "http":
        return HttpCRMTransport(settings.crm_base_url, api_token=settings.crm_api_token)
    return FixtureCRMTransport()


def build_mcp_server(settings: AppSettings) -> MinimalMCPServer:
    connector = build_crm_connector(settings)
    return MinimalMCPServer(crm_connector=connector)


@lru_cache(maxsize=1)
def get_workflow() -> CustomerSupportWorkflow:
    settings = get_settings()
    connector = build_crm_connector(settings)
    tools = ToolGateway(crm_connector=connector)
    return CustomerSupportWorkflow(tools=tools)


@lru_cache(maxsize=1)
def get_mcp_server() -> MinimalMCPServer:
    return build_mcp_server(get_settings())
