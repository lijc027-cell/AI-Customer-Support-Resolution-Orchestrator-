"""Application settings for runtime dependency selection."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class AppSettings:
    crm_transport: str = "fixture"
    crm_base_url: str = "http://localhost:8081"
    crm_api_token: str | None = None
    crm_timeout_seconds: float = 1.5
    crm_max_retries: int = 2

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "AppSettings":
        source = env or os.environ
        return cls(
            crm_transport=source.get("CSR_CRM_TRANSPORT", "fixture"),
            crm_base_url=source.get("CSR_CRM_BASE_URL", "http://localhost:8081"),
            crm_api_token=source.get("CSR_CRM_API_TOKEN"),
            crm_timeout_seconds=float(source.get("CSR_CRM_TIMEOUT_SECONDS", "1.5")),
            crm_max_retries=int(source.get("CSR_CRM_MAX_RETRIES", "2")),
        )
