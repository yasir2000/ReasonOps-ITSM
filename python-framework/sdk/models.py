from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Dashboard:
    services: int
    offerings: int
    service_level: Dict[str, Any]
    security: Dict[str, Any]
    suppliers: Dict[str, Any]
    financials: Dict[str, Any]
    history: Dict[str, Any]

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Dashboard":
        return Dashboard(
            services=d.get("services", 0),
            offerings=d.get("offerings", 0),
            service_level=d.get("service_level", {}),
            security=d.get("security", {}),
            suppliers=d.get("suppliers", {}),
            financials=d.get("financials", {}),
            history=d.get("history", {}),
        )


@dataclass
class MonthlySummary:
    month: str
    penalties: Dict[str, Any]
    chargebacks: Dict[str, Any]
    agent_decisions: Dict[str, Any]

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "MonthlySummary":
        return MonthlySummary(
            month=d.get("month", ""),
            penalties=d.get("penalties", {}),
            chargebacks=d.get("chargebacks", {}),
            agent_decisions=d.get("agent_decisions", {}),
        )


@dataclass
class SLMMetrics:
    period_days: int
    availability_pct: float
    error_budget: Dict[str, Any]
    mttr_minutes: Optional[float]
    mtbf_hours: Optional[float]

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "SLMMetrics":
        return SLMMetrics(
            period_days=d.get("period_days", 30),
            availability_pct=float(d.get("availability_pct", 0.0)),
            error_budget=d.get("error_budget", {}),
            mttr_minutes=d.get("mttr_minutes"),
            mtbf_hours=d.get("mtbf_hours"),
        )
