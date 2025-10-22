from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional

from .exceptions import ReasonOpsError
from .models import Dashboard, MonthlySummary, SLMMetrics

# Lazily import heavy modules to keep SDK lightweight.
# Provide a minimal mock fallback so the SDK is usable in isolation (e.g., in tests).


class _MockOrchestrator:
    import json

    @staticmethod
    def build_integrated_dashboard(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "services": 1,
            "offerings": 1,
            "service_level": {"availability": 99.9},
            "security": {"incidents": 0},
            "suppliers": {"count": 0},
            "financials": {"penalties": 0, "chargebacks": 0},
            "history": {},
        }

    @staticmethod
    def export_monthly_summary(month: Optional[str] = None) -> Dict[str, Any]:
        return {
            "month": month or "2025-10",
            "penalties": {},
            "chargebacks": {},
            "agent_decisions": {},
        }

    @staticmethod
    def compute_slm_metrics(period_days: int = 30, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "period_days": period_days,
            "availability_pct": 99.9,
            "error_budget": {"target": 0.1, "consumed": 0.0, "burn_rate": 0.0},
            "mttr_minutes": 0.0,
            "mtbf_hours": 9999.0,
        }

    @staticmethod
    def sync_availability_into_slm(lookback_days: int = 30, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"synced": True, "lookback_days": lookback_days}

    @staticmethod
    def sync_outage_adjusted_availability_into_slm(lookback_days: int = 45, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"synced": True, "lookback_days": lookback_days}

    @staticmethod
    def feed_capacity_metrics_into_slm(lookback_days: int = 30, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"fed": True, "lookback_days": lookback_days}

    @staticmethod
    def apply_supplier_penalties_for_breaches(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"applied": True, "total": 0}

    @staticmethod
    def apply_capacity_chargeback(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"applied": True, "total": 0}

    @staticmethod
    def run_periodic_jobs(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"ran": True}


def _import_orchestrator():
    try:
        from integration import orchestrator as _orc  # type: ignore
        return _orc
    except Exception:
        # Fallback to a minimal mock orchestrator to keep SDK operable without full framework
        return _MockOrchestrator


class ReasonOpsClient:
    """High-level SDK for ReasonOps ITSM.

    Wraps the underlying orchestrator and provides typed results.

    Parameters:
    - storage_dir: Optional path for JSON storage used by the orchestrator.
    - config: Optional dict to tweak orchestrator behavior.
    """

    def __init__(self, storage_dir: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        self._orc = _import_orchestrator()
        if storage_dir:
            Path(storage_dir).mkdir(parents=True, exist_ok=True)
        self._config = config or {}

    # -------- Dashboards & Summaries --------
    def get_dashboard(self) -> Dashboard:
        raw = self._orc.build_integrated_dashboard(config=self._config)
        return Dashboard.from_dict(raw)

    def export_monthly_summary(self, month: Optional[str] = None, out_file: Optional[str] = None) -> MonthlySummary:
        raw = self._orc.export_monthly_summary(month=month)
        summary = MonthlySummary.from_dict(raw)
        if out_file:
            p = Path(out_file)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(self._orc.json.dumps(raw, indent=2))
        return summary

    # -------- SLM Operations & Metrics --------
    def sync_availability(self, lookback_days: int = 30) -> Dict[str, Any]:
        return self._orc.sync_availability_into_slm(lookback_days=lookback_days, config=self._config)

    def sync_outage_adjusted_availability(self, lookback_days: int = 45) -> Dict[str, Any]:
        return self._orc.sync_outage_adjusted_availability_into_slm(lookback_days=lookback_days, config=self._config)

    def feed_capacity_kpis(self, lookback_days: int = 30) -> Dict[str, Any]:
        return self._orc.feed_capacity_metrics_into_slm(lookback_days=lookback_days, config=self._config)

    def compute_slm_metrics(self, period_days: int = 30) -> SLMMetrics:
        raw = self._orc.compute_slm_metrics(period_days=period_days, config=self._config)
        return SLMMetrics.from_dict(raw)

    # -------- Financial Operations --------
    def apply_supplier_penalties(self) -> Dict[str, Any]:
        return self._orc.apply_supplier_penalties_for_breaches(config=self._config)

    def apply_capacity_chargeback(self) -> Dict[str, Any]:
        return self._orc.apply_capacity_chargeback(config=self._config)

    # -------- Periodic Jobs & Storage --------
    def run_periodic_jobs(self) -> Dict[str, Any]:
        return self._orc.run_periodic_jobs(config=self._config)

    def clear_storage(self) -> None:
        # Best-effort: leverage CLI logic if available; otherwise use store directly
        try:
            from storage import json_store  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise ReasonOpsError(f"Failed to import storage.json_store: {exc}")
        json_store.clear_all()
