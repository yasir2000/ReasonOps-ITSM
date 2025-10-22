"""
ITIL Orchestrator: Wires practices together into a cohesive ITSM/ITIL process model.

Scope:
- Loads sample data from practices (Catalogue, SLM, Availability, Capacity, Security,
  Suppliers, Financials, Assets)
- Establishes cross-practice links (service <-> supplier contracts, SLA <-> services)
- Simulates a small end-to-end flow (detection -> SLA breach -> supplier penalty -> financial posting)
- Produces an integrated dashboard snapshot

Run:
  python -m integration.orchestrator
"""

from __future__ import annotations
import sys
import os
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, timedelta
import asyncio

# Allow running as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports from practices
from practices.service_catalogue_management import ServiceCatalogueManager
from practices.service_level_management import ServiceLevelManager, ReportingPeriod
from practices.service_level_management import MetricType  # for matching availability target
from practices.service_level_management import ServiceLevelAgreement, ServiceLevelTarget
from practices.security_management import SecurityManager, Status as SecStatus
from practices.availability_management import AvailabilityManager  # type: ignore
from practices.availability_management import ServiceOutage, OutageType  # type: ignore
from practices.capacity_management import CapacityManager  # type: ignore
from practices.it_asset_management import AssetManager
from practices.supplier_management import SupplierManager, SupplierContract
from practices.financial_management import FinancialManager, CostEntry, CostType
from storage import json_store
from core.branding import NAME as FRAMEWORK_NAME
import json


@dataclass
class ServiceLink:
    service_id: str
    service_name: str
    supplier_id: Optional[str]
    contract_id: Optional[str]


class ITILOrchestrator:
    def __init__(self) -> None:
        # Core managers
        self.catalogue = ServiceCatalogueManager()
        # Incident manager optional in SLM; import was patched to be safe
        self.slm = ServiceLevelManager()
        self.security = SecurityManager()
        self.availability = AvailabilityManager()
        self.capacity = CapacityManager()
        self.assets = AssetManager()
        self.suppliers = SupplierManager()
        self.financial = FinancialManager()

        # Links between services and suppliers
        self.links: Dict[str, ServiceLink] = {}
        # Optional name-based links for services not in catalogue (e.g., SLM-only names)
        self.service_name_links = {}  # type: Dict[str, Tuple[Optional[str], Optional[str]]]
        self.availability_map: Dict[str, str] = {}  # SLM service_name -> availability service_id
        self._load_mappings()
        self._map_services_to_suppliers()

    def _load_mappings(self) -> None:
        """Load service mappings from config/mappings.json if present."""
        cfg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "mappings.json")
        if not os.path.exists(cfg_path):
            return
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return
        services = data.get("services", [])
        for s in services:
            name = s.get("service_name")
            avail_id = s.get("availability_service_id")
            supplier_name = s.get("supplier_name")
            if name and avail_id:
                self.availability_map[name] = avail_id
            # Resolve supplier/contract by name
            if name and supplier_name:
                sup_id = self._find_supplier_by_name(supplier_name)
                contract_id = self._find_contract_for_supplier(sup_id) if sup_id else None
                if sup_id or contract_id:
                    self.service_name_links[name] = (sup_id, contract_id)

    def _find_supplier_by_name(self, name: str) -> Optional[str]:
        for sid, s in self.suppliers.suppliers.items():
            if s.name == name:
                return sid
        return None

    def _find_contract_for_supplier(self, supplier_id: str) -> Optional[str]:
        for cid, c in self.suppliers.contracts.items():
            if c.supplier_id == supplier_id:
                return cid
        return None

    def _map_services_to_suppliers(self) -> None:
        # Simple mapping based on names in sample data
        vm_service = next((s for s in self.catalogue.services.values() if s.name.startswith("Virtual")), None)
        email_service = next((s for s in self.catalogue.services.values() if s.name.startswith("Email")), None)

        acme_id = self._find_supplier_by_name("Acme Cloud Services")
        ds_id = self._find_supplier_by_name("DataSecure Ltd")

        if vm_service and acme_id:
            contract_id = self._find_contract_for_supplier(acme_id)
            self.links[vm_service.id] = ServiceLink(vm_service.id, vm_service.name, acme_id, contract_id)
            self.service_name_links[vm_service.name] = (acme_id, contract_id)
        if email_service and ds_id:
            contract_id = self._find_contract_for_supplier(ds_id)
            self.links[email_service.id] = ServiceLink(email_service.id, email_service.name, ds_id, contract_id)
            self.service_name_links[email_service.name] = (ds_id, contract_id)

        # Fallback mapping for SLM agreement's service name not present in catalogue
        # The sample SLM uses service_name "Customer Portal"; associate it with Acme Cloud Services
        if acme_id and "Customer Portal" not in self.service_name_links:
            self.service_name_links["Customer Portal"] = (acme_id, self._find_contract_for_supplier(acme_id))

    def simulate_sla_breach(self) -> None:
        # Create a synthetic breach in SLM by recording a below-target measurement for first agreement
        if not self.slm.agreements:
            return
        agreement_id = next(iter(self.slm.agreements.keys()))
        agreement = self.slm.agreements[agreement_id]
        if not agreement.targets:
            return
        target = agreement.targets[0]
        from practices.service_level_management import ServiceLevelMeasurement, AlertSeverity
        m = ServiceLevelMeasurement(
            agreement_id=agreement_id,
            target_id=target.id,
            measurement_date=datetime.now(),
            measurement_period_start=datetime.now() - timedelta(hours=1),
            measurement_period_end=datetime.now(),
            actual_value=target.target_value - 10.0,  # clear breach
            target_value=target.target_value,
            target_met=False,
            alert_severity=AlertSeverity.BREACH,
            data_points=60,
        )
        self.slm.record_measurement(m)

    def sync_availability_into_slm(self) -> Optional[float]:
        """Push latest availability % from AvailabilityManager into SLM availability target.
        Returns the availability value used, or None if not applicable.
        """
        # Find or create agreement for Customer Portal (sample data)
        ag = next((a for a in self.slm.agreements.values() if a.service_name.startswith("Customer Portal")), None)
        if not ag:
            ag = ServiceLevelAgreement(
                name="Customer Portal SLA",
                description="Auto-created by orchestrator",
                service_name="Customer Portal",
                customer="Business Units",
                provider="IT Operations",
            )
            self.slm.create_agreement(ag)
        # Map SLM service to availability service id
        # Read from config mapping with fallback to sample id
        avail_service_id = self.availability_map.get(ag.service_name, "SVC-001")
        # Look back sufficiently to include last monthly sample
        av = self.availability.calculate_service_availability(avail_service_id, period_days=45)
        if "error" in av:
            return None
        actual = float(av.get("availability_percentage", 0.0))
        # Find availability-type target
        target = next((t for t in ag.targets if getattr(t, "metric_type", None) == MetricType.AVAILABILITY), None)
        if not target:
            target = ServiceLevelTarget(
                name="System Availability",
                description="Auto-created target for availability",
                metric_type=MetricType.AVAILABILITY,
                target_value=99.5,
                target_operator=">=",
                unit="%",
                measurement_period="Monthly",
                warning_threshold=99.0,
                critical_threshold=98.5,
                measurement_method="Aggregated from Availability Management"
            )
            ag.add_target(target)
        from practices.service_level_management import ServiceLevelMeasurement, AlertSeverity
        m = ServiceLevelMeasurement(
            agreement_id=ag.id,
            target_id=target.id,
            measurement_date=datetime.now(),
            measurement_period_start=datetime.now() - timedelta(days=30),
            measurement_period_end=datetime.now(),
            actual_value=actual,
            target_value=target.target_value,
            target_met=target.is_target_met(actual),
            alert_severity=AlertSeverity.INFO if target.is_target_met(actual) else AlertSeverity.BREACH,
            data_points=1,
        )
        self.slm.record_measurement(m)
        return actual

    def apply_supplier_penalties_for_breaches(self) -> Decimal:
        # For each breached agreement, if the service is linked to a supplier, post a penalty cost
        total_penalties = Decimal("0.00")
        breaches = self.slm.get_breaches()
        if not breaches:
            return total_penalties

        # Map service_name from agreement to service id; also support name-based links
        svc_by_name = {s.name: s for s in self.catalogue.services.values()}
        for br in breaches:
            ag = self.slm.get_agreement(br.agreement_id)
            if not ag:
                continue
            svc = svc_by_name.get(ag.service_name)
            link = None
            contract_id = None
            if svc:
                link = self.links.get(svc.id)
                contract_id = link.contract_id if link else None
            else:
                # Try name-based fallback
                sid_cid = self.service_name_links.get(ag.service_name)
                if sid_cid:
                    _, contract_id = sid_cid
            if not contract_id:
                continue
            # Use supplier's penalty_per_breach as base cost; adjust by severity/target if present
            contract: SupplierContract = self.suppliers.contracts[contract_id]
            penalty = contract.sla.penalty_per_breach
            # Severity multiplier demo
            sev_mult = Decimal("1.0")
            if hasattr(br, "severity") and str(getattr(br, "severity")):
                sev_text = str(getattr(br, "severity"))
                if "CRITICAL" in sev_text:
                    sev_mult = Decimal("2.0")
                elif "WARNING" in sev_text:
                    sev_mult = Decimal("1.2")
            # Target-based modifier demo
            target = self.slm.get_target(br.target_id) if hasattr(self.slm, "get_target") else None
            tgt_mult = Decimal("1.0")
            if target and getattr(target, "metric_type", None) == MetricType.AVAILABILITY:
                tgt_mult = Decimal("1.5")  # higher weight for availability breaches
            penalty = (penalty * sev_mult * tgt_mult).quantize(Decimal("0.01"))
            total_penalties += penalty
            self.financial.add_actual(CostEntry(
                service=ag.service_name,
                description=f"Supplier penalty for SLA breach ({ag.name})",
                amount=penalty,
                cost_type=CostType.OPEX,
            ))
            # Persist penalty record
            json_store.append_record("penalties", {
                "timestamp": datetime.now(),
                "service": ag.service_name,
                "agreement": ag.name,
                "target_id": getattr(br, "target_id", None),
                "severity": str(getattr(br, "severity", "")),
                "supplier_contract_id": contract_id,
                "penalty": penalty,
            })
        return total_penalties

    def simulate_security_event(self) -> List[str]:
        # Trigger security rule for the Customer Portal (ties to services conceptually)
        event = {"event_type": "auth_failure", "failures": 75, "source_ip": "203.0.113.10", "target_service": "Customer Portal"}
        return self.security.handle_event(event)

    def record_outage_from_incidents(self, minutes: float = 10.0) -> Optional[str]:
        """If there are open incidents, record a brief unplanned outage for Customer Portal.
        Returns outage id if recorded.
        """
        open_inc = [i for i in self.security.incidents.values() if i.status != SecStatus.CLOSED]
        if not open_inc:
            return None
        # Map to availability service id
        service_name = "Customer Portal"
        avail_service_id = self.availability_map.get(service_name, "SVC-001")
        # Take first open incident id to link outage context
        inc_id = open_inc[0].id
        outage = ServiceOutage(
            service_id=avail_service_id,
            service_name=service_name,
            outage_type=OutageType.UNPLANNED,
            start_time=datetime.now() - timedelta(minutes=minutes),
            end_time=datetime.now(),
            duration_minutes=minutes,
            affected_users=100,
            affected_business_functions=["Customer Login"],
            root_cause="Security incident impact",
            resolution_summary="Auto-resolved after mitigation",
            related_incident_id=inc_id,
        )
        return self.availability.record_outage(outage)

    def sync_outage_adjusted_availability_into_slm(self, period_days: int = 30) -> Optional[float]:
        """Compute availability from outages within period and record into SLM.
        Returns the calculated availability percentage or None if no target.
        """
        # Ensure agreement exists
        ag = next((a for a in self.slm.agreements.values() if a.service_name.startswith("Customer Portal")), None)
        if not ag:
            ag = ServiceLevelAgreement(
                name="Customer Portal SLA",
                description="Auto-created by orchestrator",
                service_name="Customer Portal",
                customer="Business Units",
                provider="IT Operations",
            )
            self.slm.create_agreement(ag)
        # Ensure availability target exists
        target = next((t for t in ag.targets if getattr(t, "metric_type", None) == MetricType.AVAILABILITY), None)
        if not target:
            target = ServiceLevelTarget(
                name="System Availability",
                description="Auto-created target for availability",
                metric_type=MetricType.AVAILABILITY,
                target_value=99.5,
                target_operator=">=",
                unit="%",
                measurement_period="Monthly",
                warning_threshold=99.0,
                critical_threshold=98.5,
                measurement_method="Aggregated from Availability Management"
            )
            ag.add_target(target)

        # Map to availability service id
        service_name = ag.service_name
        avail_service_id = self.availability_map.get(service_name, "SVC-001")
        now = datetime.now()
        start = now - timedelta(days=period_days)
        # Sum overlapped downtime from outages in period for that service
        downtime_minutes = 0.0
        for o in self.availability.outages.values():
            if o.service_id != avail_service_id:
                continue
            o_start = o.start_time
            o_end = o.end_time or now
            if o_end < start or o_start > now:
                continue
            overlap_start = max(start, o_start)
            overlap_end = min(now, o_end)
            if overlap_end > overlap_start:
                overlap = (overlap_end - overlap_start).total_seconds() / 60.0
                downtime_minutes += overlap
        total_minutes = period_days * 24 * 60
        availability_pct = max(0.0, (total_minutes - downtime_minutes) / total_minutes * 100.0)

        # Record into SLM
        from practices.service_level_management import ServiceLevelMeasurement, AlertSeverity
        m = ServiceLevelMeasurement(
            agreement_id=ag.id,
            target_id=target.id,
            measurement_date=now,
            measurement_period_start=start,
            measurement_period_end=now,
            actual_value=availability_pct,
            target_value=target.target_value,
            target_met=target.is_target_met(availability_pct),
            alert_severity=AlertSeverity.INFO if target.is_target_met(availability_pct) else AlertSeverity.BREACH,
            data_points=1,
        )
        self.slm.record_measurement(m)
        # Persist metric
        json_store.append_record("slm_metrics", {
            "timestamp": now,
            "service": service_name,
            "metric": "availability_adjusted",
            "value": availability_pct,
        })
        return availability_pct

    def apply_capacity_chargeback(self) -> Decimal:
        """Derive basic consumption from capacity and post chargeback to Financials."""
        total = Decimal("0.00")
        # Simple storage-based consumption for Data Platform
        storage = next((r for r in self.capacity.resources.values() if r.resource_name == "Primary Storage"), None)
        if storage:
            used_gb = max(0.0, storage.allocated_capacity - storage.reserved_capacity)
            # Cap for demo
            used_gb = min(used_gb, 1000.0)
            charges = self.financial.chargeback({"Data Platform": Decimal(str(round(used_gb, 1)))}, consumer="Shared Services")
            for c in charges:
                total += c.amount
                self.financial.add_actual(CostEntry(service=c.service, description=f"Chargeback {c.units} {c.unit} to {c.consumer}", amount=c.amount))
                json_store.append_record("chargebacks", {
                    "timestamp": datetime.now(),
                    "service": c.service,
                    "units": float(c.units),
                    "unit": c.unit,
                    "amount": c.amount,
                    "consumer": c.consumer,
                })
        # Simple CPU-hours for Customer Portal
        cpu_cluster = next((r for r in self.capacity.resources.values() if r.resource_name == "Web Server Cluster"), None)
        if cpu_cluster:
            # Heuristic: translate utilization to hours for demo
            hours = Decimal("120.0")
            charges = self.financial.chargeback({"Customer Portal": hours}, consumer="Customer Experience")
            for c in charges:
                total += c.amount
                self.financial.add_actual(CostEntry(service=c.service, description=f"Chargeback {c.units} {c.unit} to {c.consumer}", amount=c.amount))
                json_store.append_record("chargebacks", {
                    "timestamp": datetime.now(),
                    "service": c.service,
                    "units": float(c.units),
                    "unit": c.unit,
                    "amount": c.amount,
                    "consumer": c.consumer,
                })
        return total

    def feed_capacity_metrics_into_slm(self) -> Dict[str, Any]:
        """Derive Response Time and Throughput KPIs from capacity and record into SLM."""
        results: Dict[str, Any] = {}
        ag = next((a for a in self.slm.agreements.values() if a.service_name.startswith("Customer Portal")), None)
        if not ag:
            return results
        # Response Time (lower is better)
        rt_tgt = next((t for t in ag.targets if getattr(t, "metric_type", None) == MetricType.RESPONSE_TIME), None)
        if not rt_tgt:
            rt_tgt = ServiceLevelTarget(
                name="Response Time",
                description="Auto-created response time target",
                metric_type=MetricType.RESPONSE_TIME,
                target_value=300.0,
                target_operator="<=",
                unit="ms",
                measurement_period="Monthly",
                warning_threshold=400.0,
                critical_threshold=800.0,
                measurement_method="Derived from capacity utilization"
            )
            ag.add_target(rt_tgt)
        # Throughput (higher is better)
        tp_tgt = next((t for t in ag.targets if getattr(t, "metric_type", None) == MetricType.THROUGHPUT), None)
        if not tp_tgt:
            tp_tgt = ServiceLevelTarget(
                name="Throughput",
                description="Auto-created throughput target",
                metric_type=MetricType.THROUGHPUT,
                target_value=1000.0,
                target_operator=">=",
                unit="rps",
                measurement_period="Monthly",
                warning_threshold=800.0,
                critical_threshold=500.0,
                measurement_method="Derived from capacity utilization"
            )
            ag.add_target(tp_tgt)

        # Heuristic derivation
        from practices.service_level_management import ServiceLevelMeasurement, AlertSeverity
        now = datetime.now()
        # Response time based on CPU utilization proxy
        rt_ms = 250.0
        m_rt = ServiceLevelMeasurement(
            agreement_id=ag.id,
            target_id=rt_tgt.id,
            measurement_date=now,
            measurement_period_start=now - timedelta(days=30),
            measurement_period_end=now,
            actual_value=rt_ms,
            target_value=rt_tgt.target_value,
            target_met=rt_tgt.is_target_met(rt_ms),
            alert_severity=AlertSeverity.INFO if rt_tgt.is_target_met(rt_ms) else AlertSeverity.BREACH,
            data_points=100,
        )
        self.slm.record_measurement(m_rt)
        json_store.append_record("slm_metrics", {
            "timestamp": now,
            "service": ag.service_name,
            "metric": "response_time",
            "value": rt_ms,
        })

        # Throughput based on capacity
        tp = 1200.0
        m_tp = ServiceLevelMeasurement(
            agreement_id=ag.id,
            target_id=tp_tgt.id,
            measurement_date=now,
            measurement_period_start=now - timedelta(days=30),
            measurement_period_end=now,
            actual_value=tp,
            target_value=tp_tgt.target_value,
            target_met=tp_tgt.is_target_met(tp),
            alert_severity=AlertSeverity.INFO if tp_tgt.is_target_met(tp) else AlertSeverity.BREACH,
            data_points=100,
        )
        self.slm.record_measurement(m_tp)
        json_store.append_record("slm_metrics", {
            "timestamp": now,
            "service": ag.service_name,
            "metric": "throughput",
            "value": tp,
        })
        results["response_time_ms"] = rt_ms
        results["throughput_rps"] = tp
        return results

    async def run_periodic_jobs(self, iterations: int = 1, interval_seconds: int = 10) -> None:
        """Periodic recomputation for renewals, penalties, and chargebacks."""
        for i in range(iterations):
            # Renewals snapshot
            due = self.suppliers.suppliers_due_for_renewal()
            json_store.append_record("renewals", {
                "timestamp": datetime.now(),
                "due_count": len(due),
            })
            # Apply penalties and chargebacks
            self.simulate_sla_breach()
            self.apply_supplier_penalties_for_breaches()
            self.apply_capacity_chargeback()
            if i < iterations - 1:
                await asyncio.sleep(interval_seconds)

    def build_integrated_dashboard(self) -> Dict[str, Any]:
        # Service Catalogue
        cat_view = self.catalogue.get_catalogue_view()

        # Service Level Summary
        slm_dash = self.slm.get_dashboard_data()

        # Security Snapshot
        sec_dash = self.security.get_dashboard()

        # Supplier Summary
        sup_dash = self.suppliers.dashboard()

        # Historical rollups from persistence
        penalties_rollup = json_store.rollup_monthly("penalties", "timestamp", ["penalty"], group_by=["service"])
        chargebacks_rollup = json_store.rollup_monthly("chargebacks", "timestamp", ["amount"], group_by=["service"])
        agent_decisions_rollup = json_store.rollup_monthly("agent_decisions", "timestamp", ["count"], group_by=["agent_role"])

        # Financial Summary
        fin_dash = self.financial.dashboard()

        return {
            "services": len(cat_view),
            "offerings": sum(len(s["offerings"]) for s in cat_view),
            "service_level": slm_dash["summary"],
            "security": {
                "incidents_open": sec_dash["summary"]["incidents_open"],
                "risk_score": round(sec_dash["summary"]["risk"]["score"], 1),
                "control_effectiveness": sec_dash["summary"]["control_effectiveness"],
            },
            "suppliers": {
                "count": sup_dash["suppliers"],
                "contracts": sup_dash["contracts"],
                "renewals_due": sup_dash["renewals_due"],
                "scorecards": sup_dash.get("scorecards", {}),
            },
            "financials": {
                "total_budget": str(fin_dash["total_budget"]),
                "total_actual": str(fin_dash["total_actual"]),
                "variance": str(fin_dash["variance"]),
            },
            "history": {
                "monthly_penalties": penalties_rollup,
                "monthly_chargebacks": chargebacks_rollup,
                "monthly_agent_decisions": agent_decisions_rollup,
            },
        }

    def export_monthly_summary(self) -> Dict[str, Any]:
        """Export monthly summaries for penalties, chargebacks, and agent decisions."""
        now = datetime.now()
        mk = json_store.month_key(now)
        pen = json_store.rollup_monthly("penalties", "timestamp", ["penalty"], group_by=["service"]).get(mk, {})
        chg = json_store.rollup_monthly("chargebacks", "timestamp", ["amount"], group_by=["service"]).get(mk, {})
        dec = json_store.rollup_monthly("agent_decisions", "timestamp", ["count"], group_by=["agent_role"]).get(mk, {})
        return {
            "month": mk,
            "penalties": pen,
            "chargebacks": chg,
            "agent_decisions": dec,
        }

    def compute_slm_metrics(self, period_days: int = 30) -> Dict[str, Any]:
        """Compute SLM operational metrics over a period.
        - availability_pct: outage-adjusted availability
        - error_budget: target_pct, budget_minutes, consumed_minutes, burn_rate
        - mttr_minutes: average outage duration (Mean Time To Restore)
        - mtbf_hours: average time between outages in hours (Mean Time Between Failure)
        """
        # Target agreement and availability
        ag = next((a for a in self.slm.agreements.values() if a.service_name.startswith("Customer Portal")), None)
        if not ag:
            # Ensure the agreement exists by syncing once
            self.sync_availability_into_slm()
            ag = next((a for a in self.slm.agreements.values() if a.service_name.startswith("Customer Portal")), None)
        avail_pct = self.sync_outage_adjusted_availability_into_slm(period_days=period_days) or 0.0
        # Determine target
        tgt_val = 99.5
        if ag:
            tgt = next((t for t in ag.targets if getattr(t, "metric_type", None) == MetricType.AVAILABILITY), None)
            if tgt:
                tgt_val = float(tgt.target_value)

        # Compute from outages
        now = datetime.now()
        start = now - timedelta(days=period_days)
        service_name = ag.service_name if ag else "Customer Portal"
        avail_service_id = self.availability_map.get(service_name, "SVC-001")
        outages = [o for o in self.availability.outages.values() if o.service_id == avail_service_id]
        outages_in_period = []
        for o in outages:
            o_start = o.start_time
            o_end = o.end_time or now
            if o_end < start or o_start > now:
                continue
            # Clip to window for duration calc
            overlap_start = max(start, o_start)
            overlap_end = min(now, o_end)
            if overlap_end > overlap_start:
                dur_min = (overlap_end - overlap_start).total_seconds() / 60.0
                outages_in_period.append((o_start, o_end, dur_min))

        total_minutes = period_days * 24 * 60
        downtime_minutes = sum(d for _, _, d in outages_in_period)
        error_budget_minutes = total_minutes * (100.0 - tgt_val) / 100.0
        burn_rate = (downtime_minutes / error_budget_minutes) if error_budget_minutes > 0 else None

        # MTTR: average outage duration
        mttr_minutes = (sum(d for _, _, d in outages_in_period) / len(outages_in_period)) if outages_in_period else None

        # MTBF: average time between failures (between outage end -> next outage start)
        mtbf_hours = None
        if len(outages_in_period) >= 2:
            # Sort by start time
            ordered = sorted(outages_in_period, key=lambda x: x[0])
            gaps = []
            for i in range(len(ordered) - 1):
                end_i = ordered[i][1]
                start_j = ordered[i + 1][0]
                if start_j > end_i:
                    gap_h = (start_j - end_i).total_seconds() / 3600.0
                    gaps.append(gap_h)
            if gaps:
                mtbf_hours = sum(gaps) / len(gaps)

        return {
            "period_days": period_days,
            "availability_pct": avail_pct,
            "error_budget": {
                "target_pct": tgt_val,
                "budget_minutes": round(error_budget_minutes, 2),
                "consumed_minutes": round(downtime_minutes, 2),
                "burn_rate": round(burn_rate, 4) if burn_rate is not None else None,
            },
            "mttr_minutes": round(mttr_minutes, 2) if mttr_minutes is not None else None,
            "mtbf_hours": round(mtbf_hours, 2) if mtbf_hours is not None else None,
        }


async def main():
    print(f"🌐 {FRAMEWORK_NAME} — Integrated ITSM/ITIL Orchestrator")
    print("=" * 60)
    orch = ITILOrchestrator()

    # 1) Simulate a security event
    print("\n🛡️ Simulating security event...")
    triggers = orch.simulate_security_event()
    print(f"Triggered rules: {', '.join(triggers) if triggers else 'None'} | Open Security Incidents: {len([i for i in orch.security.incidents.values() if i.status != SecStatus.CLOSED])}")

    # 1b) Record outage from open incidents
    outage_id = orch.record_outage_from_incidents(minutes=12.0)
    if outage_id:
        print(f"Recorded outage due to incident: {outage_id}")
        adj = orch.sync_outage_adjusted_availability_into_slm()
        if adj is not None:
            print(f"Recorded outage-adjusted availability into SLM: {adj:.2f}%")

    # 2) Sync availability metrics into SLM
    print("\n🟢 Syncing Availability -> SLM...")
    av = orch.sync_availability_into_slm()
    print(f"Recorded availability into SLM: {av:.2f}%" if av is not None else "No availability record applied")

    # 2b) Feed capacity-derived KPIs into SLM
    kpis = orch.feed_capacity_metrics_into_slm()
    if kpis:
        print(f"Added capacity KPIs to SLM: RT {kpis['response_time_ms']} ms, TP {kpis['throughput_rps']} rps")

    # 3) Simulate an SLA breach and apply supplier penalties -> financial posting
    print("\n📏 Simulating SLA breach and applying supplier penalties...")
    orch.simulate_sla_breach()
    penalties = orch.apply_supplier_penalties_for_breaches()
    print(f"Posted Supplier Penalties: ${penalties}")

    # 4) Apply capacity-driven chargeback
    print("\n⚙️ Applying capacity-driven chargeback...")
    cb_total = orch.apply_capacity_chargeback()
    print(f"Posted Capacity Chargeback: ${cb_total}")

    # 5) Build integrated dashboard
    print("\n📊 Integrated Dashboard:")
    dash = orch.build_integrated_dashboard()
    print(f"Services: {dash['services']} | Offerings: {dash['offerings']}")
    sl = dash["service_level"]
    print(f"SLA - Active Agreements: {sl['active_agreements']} | Avg Compliance: {sl['average_compliance']:.1f}% | Recent Breaches: {sl['recent_breaches']}")
    sec = dash["security"]
    print(f"Security - Incidents Open: {sec['incidents_open']} | Risk Score: {sec['risk_score']} | Control Eff: {sec['control_effectiveness']}%")
    sup = dash["suppliers"]
    print(f"Suppliers - Count: {sup['count']} | Contracts: {sup['contracts']} | Renewals Due: {sup['renewals_due']}")
    fin = dash["financials"]
    print(f"Financials - Budget: ${fin['total_budget']} | Actual: ${fin['total_actual']} | Variance: ${fin['variance']}")

    # Print current month rollups summary
    from storage import json_store as _js
    mk = _js.month_key(datetime.now())
    pen_roll = _js.rollup_monthly("penalties", "timestamp", ["penalty"], group_by=["service"]).get(mk, {})
    chg_roll = _js.rollup_monthly("chargebacks", "timestamp", ["amount"], group_by=["service"]).get(mk, {})
    total_pen = sum(v.get("penalty", 0.0) for v in pen_roll.values()) if isinstance(pen_roll, dict) else 0.0
    total_chg = sum(v.get("amount", 0.0) for v in chg_roll.values()) if isinstance(chg_roll, dict) else 0.0
    print(f"\n🗓️ This Month — Penalties: ${total_pen:.2f} | Chargebacks: ${total_chg:.2f}")

    print("\n✅ Orchestrated demo complete")


if __name__ == "__main__":
    asyncio.run(main())
