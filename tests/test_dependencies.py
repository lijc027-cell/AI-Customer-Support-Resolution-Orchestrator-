from customer_support_resolution.connectors.crm import FixtureCRMTransport, HttpCRMTransport
from customer_support_resolution.dependencies import build_crm_connector
from customer_support_resolution.settings import AppSettings


def test_app_settings_defaults_to_fixture_transport():
    settings = AppSettings.from_env({})

    assert settings.crm_transport == "fixture"
    assert settings.crm_base_url == "http://localhost:8081"
    assert settings.crm_timeout_seconds == 1.5
    assert settings.crm_max_retries == 2


def test_app_settings_reads_http_transport_from_env():
    settings = AppSettings.from_env(
        {
            "CSR_CRM_TRANSPORT": "http",
            "CSR_CRM_BASE_URL": "https://crm.internal/api",
            "CSR_CRM_API_TOKEN": "secret-token",
            "CSR_CRM_TIMEOUT_SECONDS": "3.0",
            "CSR_CRM_MAX_RETRIES": "4",
        }
    )

    assert settings.crm_transport == "http"
    assert settings.crm_base_url == "https://crm.internal/api"
    assert settings.crm_api_token == "secret-token"
    assert settings.crm_timeout_seconds == 3.0
    assert settings.crm_max_retries == 4


def test_build_crm_connector_uses_fixture_transport_by_default():
    connector = build_crm_connector(AppSettings())

    assert isinstance(connector.transport, FixtureCRMTransport)


def test_build_crm_connector_uses_http_transport_when_configured():
    connector = build_crm_connector(
        AppSettings(
            crm_transport="http",
            crm_base_url="https://crm.internal/api",
            crm_api_token="secret-token",
        )
    )

    assert isinstance(connector.transport, HttpCRMTransport)
    assert connector.transport.base_url == "https://crm.internal/api"
    assert connector.transport.api_token == "secret-token"
