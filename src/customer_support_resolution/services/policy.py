"""Policy engine skeleton."""

from __future__ import annotations

from customer_support_resolution.domain.models import RiskLevel


class PolicyEngine:
    """Applies the minimal approval policy for the first scaffold."""

    def requires_approval(self, risk_level: RiskLevel) -> bool:
        return risk_level == RiskLevel.HIGH
