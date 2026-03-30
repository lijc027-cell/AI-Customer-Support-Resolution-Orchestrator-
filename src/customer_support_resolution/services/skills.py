"""Skill registry skeleton."""

from __future__ import annotations


class SkillRegistry:
    """Selects a small set of support-domain skills."""

    def resolve(self, category: str, risk_level: str) -> list[str]:
        skills: list[str] = []
        if category == "billing":
            skills.append("billing-dispute-handling")
        if category == "sso":
            skills.append("enterprise-sso-troubleshooting")
        if risk_level == "high":
            skills.append("critical-incident-routing")
        return skills
