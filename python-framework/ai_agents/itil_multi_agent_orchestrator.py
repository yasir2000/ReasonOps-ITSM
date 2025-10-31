"""
Collaborative Autonomous AI Agents Orchestrator for ITIL Framework

This demo wires the CrewAI-style agents to the existing ITIL framework managers
and executes an end-to-end collaborative flow alongside the Integration Orchestrator.

Run:
  python -m ai_agents.itil_multi_agent_orchestrator
"""
from __future__ import annotations
import os
import sys
from datetime import datetime
from typing import Any, Dict

# Ensure package imports resolve
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integration.integration_manager import ITILIntegrationManager
from integration.orchestrator import ITILOrchestrator
from ai_agents import ITILAgentCrew, create_sample_incident
from ai_agents.matis_task_executor import MatisTaskExecutor
from core.branding import NAME as FRAMEWORK_NAME
from integration.event_bus import EventBus
from storage import json_store

# Practices
from practices.service_catalogue_management import ServiceCatalogueManager
from practices.service_level_management import ServiceLevelManager
from practices.security_management import SecurityManager
from practices.availability_management import AvailabilityManager
from practices.capacity_management import CapacityManager
from practices.it_asset_management import AssetManager
from practices.supplier_management import SupplierManager
from practices.financial_management import FinancialManager


class CollaborativeAgentsOrchestrator:
    def __init__(self, llm_config_file: str | None = None) -> None:
        # 1) Register practices into integration manager for tools access
        self.integration = ITILIntegrationManager()
        self._register_practices()
        self.integration.initialize_framework()

        # 2) Create the multi-agent crew (uses integration registry)
        self.agents = ITILAgentCrew(self.integration, llm_config_file=llm_config_file)

        # 3) Reuse existing integrated orchestrator for cross-practice actions
        self.itil = ITILOrchestrator()

        # 4) Event bus for autonomous reactions
        self.bus = EventBus()
        self._register_event_handlers()

        # 5) Matis Task Automation Executor for autonomous task execution
        self.matis_executor = MatisTaskExecutor()

    def _register_event_handlers(self) -> None:
        # Security Analyst reacts to new incidents
        def on_incident_created(payload):
            json_store.append_record("agent_decisions", {
                "timestamp": payload.get("timestamp"),
                "agent_role": "Security Analyst",
                "action": "Initiated containment plan",
                "incident_id": payload.get("incident_id"),
                "service": payload.get("service_name"),
                "count": 1,
            })
        # Availability Manager reacts to outages
        def on_outage_created(payload):
            json_store.append_record("agent_decisions", {
                "timestamp": payload.get("timestamp"),
                "agent_role": "Availability Manager",
                "action": "Started post-incident review",
                "outage_id": payload.get("outage_id"),
                "service": payload.get("service_name"),
                "count": 1,
            })
        # Capacity Planner reacts to capacity threshold crossed
        def on_capacity_threshold(payload):
            json_store.append_record("agent_decisions", {
                "timestamp": payload.get("timestamp"),
                "agent_role": "Capacity Planner",
                "action": "Proposed scale-up plan",
                "resource": payload.get("resource_name"),
                "service": payload.get("service_name"),
                "count": 1,
            })

        self.bus.subscribe("incident.created", on_incident_created)
        self.bus.subscribe("outage.created", on_outage_created)
        self.bus.subscribe("capacity.threshold_crossed", on_capacity_threshold)

    def _register_practices(self) -> None:
        self.integration.register_practice("service_catalogue", ServiceCatalogueManager())
        self.integration.register_practice("service_level_management", ServiceLevelManager())
        self.integration.register_practice("security_management", SecurityManager())
        self.integration.register_practice("availability_management", AvailabilityManager())
        self.integration.register_practice("capacity_management", CapacityManager())
        self.integration.register_practice("it_asset_management", AssetManager())
        self.integration.register_practice("supplier_management", SupplierManager())
        self.integration.register_practice("financial_management", FinancialManager())
        # Optional placeholders for incident/problem if not fully implemented
        class _IncidentMgmtStub:
            def get_metrics(self, period_days: int): return {"incidents": 0}
            def get_configuration(self): return {}
            def validate_configuration(self): return True
            def get_health_status(self): return {"status": "ok"}
        class _ProblemMgmtStub:
            def get_metrics(self, period_days: int): return {"problems": 0}
            def get_configuration(self): return {}
            def validate_configuration(self): return True
            def get_health_status(self): return {"status": "ok"}
        self.integration.register_practice("incident_management", _IncidentMgmtStub())
        self.integration.register_practice("problem_management", _ProblemMgmtStub())

    def run_demo(self) -> Dict[str, Any]:
        print(f"🤝 {FRAMEWORK_NAME} — Collaborative AI Agents × ITIL Orchestrator")
        print("=" * 64)

        # A) Agents analyze an incident collaboratively
        incident = create_sample_incident()
        print(f"\n📞 Sample Incident: {incident['id']} — {incident['title']}")
        crew_result = self.agents.handle_incident(incident)
        print(f"🤖 Crew status: {crew_result.get('status')} | confidence: {crew_result.get('confidence_score', 0):.2f}")
        # Emit event for agent reactions
        self.bus.publish("incident.created", {
            "timestamp": incident.get("detected_at"),
            "incident_id": incident.get("id"),
            "service_name": incident.get("service", "Customer Portal"),
        })

        # B) Orchestrator operational flow (security→outage→SLM/financials)
        print("\n🛡️ Security event + outage + SLM sync + penalties + chargeback")
        self.itil.simulate_security_event()
        outage_id = self.itil.record_outage_from_incidents(minutes=10.0)
        if outage_id:
            print(f"Recorded outage: {outage_id}")
            adj = self.itil.sync_outage_adjusted_availability_into_slm()
            print(f"Outage-adjusted availability recorded: {adj:.2f}%")
            # Emit outage event
            from datetime import datetime as _dt
            self.bus.publish("outage.created", {
                "timestamp": _dt.now().isoformat(),
                "outage_id": outage_id,
                "service_name": "Customer Portal",
            })
        av = self.itil.sync_availability_into_slm()
        print(f"Availability recorded: {av:.2f}%")
        kpis = self.itil.feed_capacity_metrics_into_slm()
        print(f"Capacity KPIs added: {kpis}")
        # Emit capacity threshold event (demo)
        from datetime import datetime as _dt
        self.bus.publish("capacity.threshold_crossed", {
            "timestamp": _dt.now().isoformat(),
            "resource_name": "Web Server Cluster",
            "service_name": "Customer Portal",
        })
        self.itil.simulate_sla_breach()
        penalties = self.itil.apply_supplier_penalties_for_breaches()
        chargebacks = self.itil.apply_capacity_chargeback()
        print(f"Financials — Penalties: ${penalties} | Chargebacks: ${chargebacks}")

        # C) Integrated dashboard
        dash = self.itil.build_integrated_dashboard()
        print("\n📊 Integrated Dashboard Snapshot:")
        print(f"Services: {dash['services']} | Offerings: {dash['offerings']}")
        sl = dash["service_level"]
        print(f"SLA - Active: {sl['active_agreements']} | Avg: {sl['average_compliance']:.1f}% | Breaches: {sl['recent_breaches']}")
        fin = dash["financials"]
        print(f"Budget: ${fin['total_budget']} | Actual: ${fin['total_actual']} | Variance: ${fin['variance']}")

        # D) Matis Task Automation Execution
        print("\n🔧 Matis Task Force Automation")
        if self.matis_executor.validate_matis_installation():
            print("✅ Matis executor validated")
            print("📋 Matis Task Automation Platform integrated successfully")
            print("� Ready for intelligent autonomous IT task execution")
            print("   - Agentless automation with SSH/WinRM transport")
            print("   - Zero-dependency execution (no Python on targets)")
            print("   - Type-safe configuration with YAML validation")
            print("   - Concurrent execution with configurable thread pools")
            print("   - Extensible plugin system for custom functionality")
        else:
            print("⚠️ Matis not available - skipping automated task execution")

        return {
            "timestamp": datetime.now().isoformat(),
            "crew_result": crew_result,
            "dashboard": dash,
        }


def main():
    orchestrator = CollaborativeAgentsOrchestrator()
    orchestrator.run_demo()
    print("\n✅ Collaborative agents demo complete")


if __name__ == "__main__":
    main()
