"""
ReasonOps ITSM CLI

Comprehensive command-line interface for the ReasonOps ITSM framework.
Provides full access to all ITIL practices, AI agents, and management operations.

Usage:
  python -m cli <command> [options]
  
Categories:
  practices    - ITIL Practice management (incident, problem, change, etc.)
  cmdb         - Configuration Management Database operations
  agents       - AI Agent orchestration and management
  matis        - Matis Task Automation Platform
  slm          - Service Level Management
  financial    - Financial management and reporting
  assets       - IT Asset management
  knowledge    - Knowledge Management System
  catalog      - Service Catalog management
  workflow     - Workflow and orchestration
  metrics      - Reporting and analytics
  config       - Configuration management
  data         - Data operations (import/export/backup)
  system       - System administration
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import asyncio
import csv
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml


# Ensure local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.branding import NAME as FRAMEWORK_NAME, VERSION as FRAMEWORK_VERSION, TAGLINE as FRAMEWORK_TAGLINE
from integration.orchestrator import ITILOrchestrator
from ai_agents.itil_multi_agent_orchestrator import CollaborativeAgentsOrchestrator
from ai_agents.matis_task_executor import MatisTaskExecutor
from storage import json_store


def _to_json_friendly(obj: Any) -> Any:
    """Convert objects to JSON-serializable format"""
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if isinstance(k, (str, int, float, bool)) or k is None:
                nk = k
            else:
                nk = str(k)
            new_dict[nk] = _to_json_friendly(v)
        return new_dict
    if isinstance(obj, list):
        return [_to_json_friendly(x) for x in obj]
    if hasattr(obj, '__dict__'):
        return _to_json_friendly(obj.__dict__)
    if hasattr(obj, 'isoformat'):  # datetime objects
        return obj.isoformat()
    return obj


def print_json(data: Dict[str, Any]) -> None:
    """Pretty print JSON data"""
    print(json.dumps(_to_json_friendly(data), indent=2, default=str))


def write_output(data: Dict[str, Any], out_path: str) -> None:
    """Write data to output file"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(_to_json_friendly(data), f, indent=2, default=str)
    print(f"✓ Output written to: {out_path}")


def print_table(data: List[Dict], headers: Optional[List[str]] = None) -> None:
    """Print data in a table format"""
    if not data:
        print("No data to display")
        return
    
    if not headers:
        headers = list(data[0].keys()) if data else []
    
    # Calculate column widths
    widths = {h: len(h) for h in headers}
    for row in data:
        for h in headers:
            value = str(row.get(h, ''))
            widths[h] = max(widths[h], len(value))
    
    # Print header
    header_line = ' | '.join(h.ljust(widths[h]) for h in headers)
    print(header_line)
    print('-' * len(header_line))
    
    # Print rows
    for row in data:
        row_line = ' | '.join(str(row.get(h, '')).ljust(widths[h]) for h in headers)
        print(row_line)


def cmd_version(args):
    """Show framework version and info"""
    print(f"🚀 {FRAMEWORK_NAME} v{FRAMEWORK_VERSION}")
    print(f"{FRAMEWORK_TAGLINE}")
    print(f"\nFeatures:")
    print(f"  • Complete ITIL 4 implementation")
    print(f"  • AI-powered multi-agent orchestration")
    print(f"  • Multi-LLM provider support (Ollama, OpenAI, etc.)")
    print(f"  • Comprehensive CLI interface")
    print(f"  • REST API and Web UI")
    print(f"  • Enterprise integration ready")
    print(f"\nFor help: python -m cli --help")
    print(f"For specific command help: python -m cli <command> --help")


def ensure_orch() -> ITILOrchestrator:
    return ITILOrchestrator()


def cmd_run_orchestrator(args):
    from integration.orchestrator import main as orchestrator_main
    import asyncio
    asyncio.run(orchestrator_main())


def cmd_run_agents(args):
    orch = CollaborativeAgentsOrchestrator(llm_config_file=args.llm_config)
    result = orch.run_demo()
    if args.json:
        print_json(result)


def cmd_dashboard(args):
    o = ensure_orch()
    dash = o.build_integrated_dashboard()
    if args.json:
        print_json(dash)
    else:
        print(f"Services: {dash['services']} | Offerings: {dash['offerings']}")
        sl = dash["service_level"]
        print(f"SLA - Active: {sl['active_agreements']} | Avg: {sl['average_compliance']:.1f}% | Breaches: {sl['recent_breaches']}")
        fin = dash["financials"]
        print(f"Budget: ${fin['total_budget']} | Actual: ${fin['total_actual']} | Variance: ${fin['variance']}")


def cmd_export_monthly(args):
    o = ensure_orch()
    summary = o.export_monthly_summary()
    if args.json:
        print_json(summary)
    if args.out:
        write_output(summary, args.out)


def cmd_jobs_run(args):
    import asyncio
    o = ensure_orch()
    asyncio.run(o.run_periodic_jobs(iterations=args.iterations, interval_seconds=args.interval))


def cmd_security_simulate(args):
    o = ensure_orch()
    triggers = o.simulate_security_event()
    print(f"Triggered: {', '.join(triggers) if triggers else 'None'}")


def cmd_outage_record(args):
    o = ensure_orch()
    outage_id = o.record_outage_from_incidents(minutes=args.minutes)
    print(outage_id or "No open incidents; outage not recorded")


def cmd_slm_sync_availability(args):
    o = ensure_orch()
    av = o.sync_availability_into_slm()
    print(json.dumps({"availability": av}, indent=2)) if args.json else print(f"Availability recorded: {av}")


def cmd_slm_sync_outage_availability(args):
    o = ensure_orch()
    pct = o.sync_outage_adjusted_availability_into_slm(period_days=args.days)
    print(json.dumps({"availability_adjusted": pct}, indent=2)) if args.json else print(f"Outage-adjusted availability: {pct}")


def cmd_slm_feed_capacity_kpis(args):
    o = ensure_orch()
    kpis = o.feed_capacity_metrics_into_slm()
    print_json(kpis) if args.json else print(f"KPIs: {kpis}")

def cmd_slm_metrics(args):
    o = ensure_orch()
    metrics = o.compute_slm_metrics(period_days=args.days)
    print_json(metrics) if args.json else print(metrics)


def cmd_fin_apply_penalties(args):
    o = ensure_orch()
    amt = o.apply_supplier_penalties_for_breaches()
    print(json.dumps({"penalties": str(amt)}, indent=2)) if args.json else print(f"Penalties: ${amt}")


def cmd_fin_apply_chargeback(args):
    o = ensure_orch()
    amt = o.apply_capacity_chargeback()
    print(json.dumps({"chargebacks": str(amt)}, indent=2)) if args.json else print(f"Chargebacks: ${amt}")


def cmd_rollups_show(args):
    mk = args.month or json_store.month_key(__import__("datetime").datetime.now())
    coll = args.collection
    roll = json_store.rollup_monthly(coll, "timestamp", args.fields, group_by=args.group_by)
    data = roll.get(mk, {})
    print_json({"month": mk, "collection": coll, "rollup": data}) if args.json else print(data)


def cmd_storage_clear(args):
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'storage', 'data')
    if not os.path.isdir(data_dir):
        print("No data directory to clear.")
        return
    if not args.yes:
        resp = input(f"Delete all JSON files in {data_dir}? [y/N]: ").strip().lower()
        if resp != 'y':
            print("Aborted.")
            return
    count = 0
    for fn in os.listdir(data_dir):
        if fn.endswith('.json'):
            try:
                os.remove(os.path.join(data_dir, fn))
                count += 1
            except Exception:
                pass
    print(f"Deleted {count} files from {data_dir}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ReasonOps ITSM", description=FRAMEWORK_TAGLINE)
    p.add_argument("command", help="Command to execute", nargs="?")
    p.add_argument("subcommand", help="Optional subcommand", nargs="?")
    p.add_argument("rest", nargs=argparse.REMAINDER)
    p.add_argument("--version", action="store_true", help="Show version")
    return p


def main():
    """Main CLI entry point with comprehensive command structure"""
    parser = argparse.ArgumentParser(
        prog="ReasonOps ITSM", 
        description=f"{FRAMEWORK_TAGLINE}\n\nComprehensive ITIL 4 framework with AI agents and multi-LLM support",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ========================================
    # SYSTEM COMMANDS
    # ========================================
    system_parser = subparsers.add_parser("system", help="System administration")
    system_sub = system_parser.add_subparsers(dest="system_cmd")
    
    # version
    version_parser = system_sub.add_parser("version", help="Show framework version and info")
    version_parser.set_defaults(func=cmd_version)
    
    # status
    status_parser = system_sub.add_parser("status", help="Show system status and health")
    status_parser.add_argument("--json", action="store_true")
    status_parser.set_defaults(func=cmd_system_status)
    
    # init
    init_parser = system_sub.add_parser("init", help="Initialize ReasonOps workspace")
    init_parser.add_argument("--path", default=".", help="Path to initialize workspace")
    init_parser.add_argument("--force", action="store_true", help="Force initialization")
    init_parser.set_defaults(func=cmd_system_init)

    # ========================================
    # PRACTICES COMMANDS
    # ========================================
    practices_parser = subparsers.add_parser("practices", help="ITIL Practice management")
    practices_sub = practices_parser.add_subparsers(dest="practice_cmd")
    
    # incident management
    incident_parser = practices_sub.add_parser("incident", help="Incident management")
    incident_sub = incident_parser.add_subparsers(dest="incident_cmd")
    
    # Create incident
    inc_create = incident_sub.add_parser("create", help="Create new incident")
    inc_create.add_argument("--title", required=True, help="Incident title")
    inc_create.add_argument("--description", help="Incident description")
    inc_create.add_argument("--caller", help="Caller ID or email")
    inc_create.add_argument("--category", help="Incident category")
    inc_create.add_argument("--impact", choices=["low", "medium", "high", "critical"], help="Impact level")
    inc_create.add_argument("--urgency", choices=["low", "medium", "high", "critical"], help="Urgency level")
    inc_create.add_argument("--json", action="store_true")
    inc_create.set_defaults(func=cmd_incident_create)
    
    # List incidents
    inc_list = incident_sub.add_parser("list", help="List incidents")
    inc_list.add_argument("--status", help="Filter by status")
    inc_list.add_argument("--priority", help="Filter by priority")
    inc_list.add_argument("--limit", type=int, default=20, help="Limit results")
    inc_list.add_argument("--json", action="store_true")
    inc_list.set_defaults(func=cmd_incident_list)
    
    # Show incident
    inc_show = incident_sub.add_parser("show", help="Show incident details")
    inc_show.add_argument("incident_id", help="Incident ID")
    inc_show.add_argument("--json", action="store_true")
    inc_show.set_defaults(func=cmd_incident_show)
    
    # Update incident
    inc_update = incident_sub.add_parser("update", help="Update incident")
    inc_update.add_argument("incident_id", help="Incident ID")
    inc_update.add_argument("--status", help="New status")
    inc_update.add_argument("--priority", help="New priority")
    inc_update.add_argument("--assignee", help="Assign to user")
    inc_update.add_argument("--comment", help="Add comment")
    inc_update.add_argument("--json", action="store_true")
    inc_update.set_defaults(func=cmd_incident_update)

    # problem management
    problem_parser = practices_sub.add_parser("problem", help="Problem management")
    problem_sub = problem_parser.add_subparsers(dest="problem_cmd")
    
    prob_create = problem_sub.add_parser("create", help="Create new problem")
    prob_create.add_argument("--title", required=True, help="Problem title")
    prob_create.add_argument("--description", help="Problem description")
    prob_create.add_argument("--related-incidents", nargs="+", help="Related incident IDs")
    prob_create.add_argument("--json", action="store_true")
    prob_create.set_defaults(func=cmd_problem_create)
    
    prob_list = problem_sub.add_parser("list", help="List problems")
    prob_list.add_argument("--status", help="Filter by status")
    prob_list.add_argument("--limit", type=int, default=20)
    prob_list.add_argument("--json", action="store_true")
    prob_list.set_defaults(func=cmd_problem_list)

    # change management
    change_parser = practices_sub.add_parser("change", help="Change management")
    change_sub = change_parser.add_subparsers(dest="change_cmd")
    
    chg_create = change_sub.add_parser("create", help="Create new change")
    chg_create.add_argument("--title", required=True, help="Change title")
    chg_create.add_argument("--description", help="Change description")
    chg_create.add_argument("--type", choices=["normal", "standard", "emergency"], default="normal")
    chg_create.add_argument("--risk", choices=["low", "medium", "high"], default="medium")
    chg_create.add_argument("--json", action="store_true")
    chg_create.set_defaults(func=cmd_change_create)
    
    chg_list = change_sub.add_parser("list", help="List changes")
    chg_list.add_argument("--status", help="Filter by status")
    chg_list.add_argument("--type", help="Filter by type")
    chg_list.add_argument("--limit", type=int, default=20)
    chg_list.add_argument("--json", action="store_true")
    chg_list.set_defaults(func=cmd_change_list)

    # ========================================
    # CMDB COMMANDS
    # ========================================
    cmdb_parser = subparsers.add_parser("cmdb", help="Configuration Management Database")
    cmdb_sub = cmdb_parser.add_subparsers(dest="cmdb_cmd")
    
    # Add CI
    ci_add = cmdb_sub.add_parser("add", help="Add configuration item")
    ci_add.add_argument("--name", required=True, help="CI name")
    ci_add.add_argument("--type", required=True, help="CI type")
    ci_add.add_argument("--class", dest="ci_class", help="CI class")
    ci_add.add_argument("--status", default="active", help="CI status")
    ci_add.add_argument("--location", help="CI location")
    ci_add.add_argument("--owner", help="CI owner")
    ci_add.add_argument("--json", action="store_true")
    ci_add.set_defaults(func=cmd_cmdb_add)
    
    # List CIs
    ci_list = cmdb_sub.add_parser("list", help="List configuration items")
    ci_list.add_argument("--type", help="Filter by CI type")
    ci_list.add_argument("--status", help="Filter by status")
    ci_list.add_argument("--limit", type=int, default=20)
    ci_list.add_argument("--json", action="store_true")
    ci_list.set_defaults(func=cmd_cmdb_list)
    
    # Show CI
    ci_show = cmdb_sub.add_parser("show", help="Show CI details")
    ci_show.add_argument("ci_id", help="CI ID")
    ci_show.add_argument("--json", action="store_true")
    ci_show.set_defaults(func=cmd_cmdb_show)
    
    # Relationships
    ci_relate = cmdb_sub.add_parser("relate", help="Create CI relationship")
    ci_relate.add_argument("source_ci", help="Source CI ID")
    ci_relate.add_argument("target_ci", help="Target CI ID")
    ci_relate.add_argument("--type", default="depends_on", help="Relationship type")
    ci_relate.add_argument("--json", action="store_true")
    ci_relate.set_defaults(func=cmd_cmdb_relate)

    # ========================================
    # AI AGENTS COMMANDS (Enhanced)
    # ========================================
    agents_parser = subparsers.add_parser("agents", help="AI Agent orchestration and management")
    agents_sub = agents_parser.add_subparsers(dest="agent_cmd")

    # run orchestrator
    orch_parser = agents_sub.add_parser("orchestrator", help="Run the integrated orchestrator demo")
    orch_parser.set_defaults(func=cmd_run_orchestrator)

    # run agents
    run_parser = agents_sub.add_parser("run", help="Execute AI agent orchestration for an event")
    run_parser.add_argument("--event-type", required=True, help="Event type (incident, capacity_alert, outage)")
    run_parser.add_argument("--event-data", required=True, help="Event data as JSON string")
    run_parser.add_argument("--llm-config", dest="llm_config", help="Path to LLM providers config file")
    run_parser.add_argument("--json", action="store_true")
    run_parser.set_defaults(func=cmd_agents_run)

    # list decisions
    decisions_parser = agents_sub.add_parser("decisions", help="List agent decision history")
    decisions_parser.add_argument("--limit", type=int, default=50, help="Max number of decisions to retrieve")
    decisions_parser.add_argument("--event-type", help="Filter by event type")
    decisions_parser.add_argument("--agent-name", help="Filter by agent name")
    decisions_parser.add_argument("--json", action="store_true")
    decisions_parser.set_defaults(func=cmd_agents_list_decisions)

    # configure LLM
    config_parser = agents_sub.add_parser("configure", help="Configure LLM provider for agents")
    config_parser.add_argument("--provider", required=True, help="LLM provider (ollama, openai, anthropic, etc.)")
    config_parser.add_argument("--model", help="Model name (e.g., llama2-7b, gpt-4)")
    config_parser.add_argument("--api-key", help="API key for provider")
    config_parser.add_argument("--temperature", type=float, default=0.7, help="Temperature (0.0-1.0)")
    config_parser.add_argument("--json", action="store_true")
    config_parser.set_defaults(func=cmd_agents_configure_llm)

    # health check
    health_parser = agents_sub.add_parser("health", help="Check health of LLM providers")
    health_parser.add_argument("--json", action="store_true")
    health_parser.set_defaults(func=cmd_agents_health)

    # list providers
    providers_parser = agents_sub.add_parser("providers", help="List available LLM providers and models")
    providers_parser.add_argument("--json", action="store_true")
    providers_parser.set_defaults(func=cmd_agents_list_providers)

    # ========================================
    # MATIS TASK AUTOMATION
    # ========================================
    matis_parser = subparsers.add_parser("matis", help="Matis Task Automation Platform")
    matis_sub = matis_parser.add_subparsers(dest="matis_cmd")

    # validate installation
    validate_parser = matis_sub.add_parser("validate", help="Validate Matis installation")
    validate_parser.set_defaults(func=cmd_matis_validate)

    # execute playbook
    execute_parser = matis_sub.add_parser("execute", help="Execute a Matis playbook")
    execute_parser.add_argument("--playbook", required=True, help="Path to playbook YAML file")
    execute_parser.add_argument("--inventory", help="Path to inventory YAML file")
    execute_parser.add_argument("--extra-vars", action="append", help="Extra variables (key=value)")
    execute_parser.add_argument("--task-id", help="Task identifier")
    execute_parser.set_defaults(func=cmd_matis_execute)

    # execute SSH playbook
    ssh_parser = matis_sub.add_parser("ssh", help="Execute playbook over SSH")
    ssh_parser.add_argument("--playbook", required=True, help="Path to playbook YAML file")
    ssh_parser.add_argument("--inventory", required=True, help="Path to inventory YAML file")
    ssh_parser.add_argument("--user", help="SSH username")
    ssh_parser.add_argument("--key", help="SSH private key path")
    ssh_parser.add_argument("--threads", type=int, default=4, help="Number of parallel threads")
    ssh_parser.add_argument("--task-id", help="Task identifier")
    ssh_parser.set_defaults(func=cmd_matis_ssh)

    # simulate execution
    simulate_parser = matis_sub.add_parser("simulate", help="Simulate playbook execution")
    simulate_parser.add_argument("--playbook", required=True, help="Path to playbook YAML file")
    simulate_parser.add_argument("--inventory", help="Path to inventory YAML file")
    simulate_parser.add_argument("--task-id", help="Task identifier")
    simulate_parser.set_defaults(func=cmd_matis_simulate)

    # show history
    history_parser = matis_sub.add_parser("history", help="Show execution history")
    history_parser.add_argument("--limit", type=int, default=10, help="Max number of results")
    history_parser.add_argument("--json", action="store_true")
    history_parser.set_defaults(func=cmd_matis_history)

    # create sample playbook
    sample_parser = matis_sub.add_parser("sample", help="Create sample playbook and inventory")
    sample_parser.add_argument("--type", choices=["incident-response", "inventory"], default="incident-response", help="Type of sample to create")
    sample_parser.add_argument("--output", help="Output directory")
    sample_parser.set_defaults(func=cmd_matis_sample)

    # generate AI playbook
    generate_parser = matis_sub.add_parser("generate", help="Generate AI-powered automation playbook")
    generate_parser.add_argument("--description", required=True, help="Description of automation requirement")
    generate_parser.add_argument("--hosts", default="all", help="Target hosts for automation")
    generate_parser.add_argument("--type", default="incident_response", choices=["incident_response", "maintenance", "deployment", "monitoring"], help="Type of automation")
    generate_parser.add_argument("--output", help="Output file path")
    generate_parser.set_defaults(func=cmd_matis_generate)

    # generate incident response
    incident_parser = matis_sub.add_parser("incident-playbook", help="Generate incident-specific response playbook")
    incident_parser.add_argument("--title", required=True, help="Incident title")
    incident_parser.add_argument("--description", required=True, help="Incident description")
    incident_parser.add_argument("--services", nargs="+", help="Affected services")
    incident_parser.add_argument("--output", help="Output file path")
    incident_parser.set_defaults(func=cmd_matis_incident_playbook)

    # ========================================
    # DASHBOARD & REPORTING
    # ========================================
    dashboard_parser = subparsers.add_parser("dashboard", help="Print integrated dashboard snapshot")
    dashboard_parser.add_argument("--json", action="store_true")
    dashboard_parser.set_defaults(func=cmd_dashboard)

    # ========================================
    # SERVICE LEVEL MANAGEMENT
    # ========================================
    slm_parser = subparsers.add_parser("slm", help="Service Level Management")
    slm_sub = slm_parser.add_subparsers(dest="slm_cmd")
    
    # sync availability
    sync_av = slm_sub.add_parser("sync-availability", help="Sync availability into SLM")
    sync_av.add_argument("--json", action="store_true")
    sync_av.set_defaults(func=cmd_slm_sync_availability)

    # sync outage availability  
    sync_outage = slm_sub.add_parser("sync-outage-availability", help="Sync outage-adjusted availability into SLM")
    sync_outage.add_argument("--days", type=int, default=30)
    sync_outage.add_argument("--json", action="store_true")
    sync_outage.set_defaults(func=cmd_slm_sync_outage_availability)

    # feed capacity KPIs
    feed_kpis = slm_sub.add_parser("feed-capacity-kpis", help="Feed capacity KPIs (RT/TP) into SLM")
    feed_kpis.add_argument("--json", action="store_true")
    feed_kpis.set_defaults(func=cmd_slm_feed_capacity_kpis)

    # compute metrics
    metrics = slm_sub.add_parser("metrics", help="Compute SLM metrics (availability, MTTR/MTBF, error budget)")
    metrics.add_argument("--days", type=int, default=30)
    metrics.add_argument("--json", action="store_true")
    metrics.set_defaults(func=cmd_slm_metrics)

    # ========================================
    # FINANCIAL MANAGEMENT
    # ========================================
    financial_parser = subparsers.add_parser("financial", help="Financial management and reporting")
    financial_sub = financial_parser.add_subparsers(dest="financial_cmd")

    # apply penalties
    penalties = financial_sub.add_parser("penalties", help="Apply supplier penalties for breach")
    penalties.add_argument("--json", action="store_true")
    penalties.set_defaults(func=cmd_fin_apply_penalties)

    # apply chargeback
    chargeback = financial_sub.add_parser("chargeback", help="Apply capacity-driven chargebacks")
    chargeback.add_argument("--json", action="store_true")
    chargeback.set_defaults(func=cmd_fin_apply_chargeback)

    # budget management
    budget = financial_sub.add_parser("budget", help="Budget management")
    budget_sub = budget.add_subparsers(dest="budget_cmd")
    
    budget_show = budget_sub.add_parser("show", help="Show budget information")
    budget_show.add_argument("--service", help="Filter by service")
    budget_show.add_argument("--json", action="store_true")
    budget_show.set_defaults(func=cmd_budget_show)

    # ========================================
    # DATA OPERATIONS
    # ========================================
    data_parser = subparsers.add_parser("data", help="Data operations (import/export/backup)")
    data_sub = data_parser.add_subparsers(dest="data_cmd")

    # export monthly
    export_monthly = data_sub.add_parser("export-monthly", help="Export current month rollups")
    export_monthly.add_argument("--json", action="store_true")
    export_monthly.add_argument("--out", help="Output file path")
    export_monthly.set_defaults(func=cmd_export_monthly)

    # rollups
    rollups = data_sub.add_parser("rollups", help="Show rollups for a collection by month")
    rollups.add_argument("--collection", required=True, help="Collection name, e.g., penalties, chargebacks, agent_decisions")
    rollups.add_argument("--fields", nargs="+", default=["amount"], help="Fields to sum, e.g., amount penalty count")
    rollups.add_argument("--group-by", nargs="+", default=["service"], help="Group-by fields, e.g., service agent_role")
    rollups.add_argument("--month", help="YYYY-MM month key (default: current)")
    rollups.add_argument("--json", action="store_true")
    rollups.set_defaults(func=cmd_rollups_show)

    # storage management
    storage_clear = data_sub.add_parser("clear", help="Delete JSON data files under storage/data")
    storage_clear.add_argument("--yes", action="store_true", help="Confirm deletion without prompt")
    storage_clear.set_defaults(func=cmd_storage_clear)

    # backup
    backup = data_sub.add_parser("backup", help="Backup data to archive")
    backup.add_argument("--path", help="Backup path")
    backup.add_argument("--compress", action="store_true", help="Compress backup")
    backup.set_defaults(func=cmd_data_backup)

    # restore
    restore = data_sub.add_parser("restore", help="Restore data from backup")
    restore.add_argument("--path", required=True, help="Backup path to restore")
    restore.add_argument("--force", action="store_true", help="Force restore")
    restore.set_defaults(func=cmd_data_restore)

    # ========================================
    # JOBS & AUTOMATION
    # ========================================
    jobs_parser = subparsers.add_parser("jobs", help="Job management and automation")
    jobs_sub = jobs_parser.add_subparsers(dest="jobs_cmd")

    # run periodic jobs
    jobs_run = jobs_sub.add_parser("run", help="Run periodic jobs")
    jobs_run.add_argument("--iterations", type=int, default=1)
    jobs_run.add_argument("--interval", type=int, default=10)
    jobs_run.set_defaults(func=cmd_jobs_run)

    # list jobs
    jobs_list = jobs_sub.add_parser("list", help="List available jobs")
    jobs_list.add_argument("--json", action="store_true")
    jobs_list.set_defaults(func=cmd_jobs_list)

    # ========================================
    # SECURITY OPERATIONS
    # ========================================
    security_parser = subparsers.add_parser("security", help="Security operations")
    security_sub = security_parser.add_subparsers(dest="security_cmd")

    # simulate event
    sec_simulate = security_sub.add_parser("simulate", help="Simulate a security event")
    sec_simulate.set_defaults(func=cmd_security_simulate)

    # audit
    sec_audit = security_sub.add_parser("audit", help="Security audit")
    sec_audit.add_argument("--type", choices=["access", "config", "data"], help="Audit type")
    sec_audit.add_argument("--json", action="store_true")
    sec_audit.set_defaults(func=cmd_security_audit)

    # ========================================
    # INCIDENT OPERATIONS  
    # ========================================
    outage_parser = subparsers.add_parser("outage", help="Outage management")
    outage_sub = outage_parser.add_subparsers(dest="outage_cmd")

    # record outage
    outage_record = outage_sub.add_parser("record", help="Record outage from open incidents")
    outage_record.add_argument("--minutes", type=float, default=10.0)
    outage_record.set_defaults(func=cmd_outage_record)

    # ========================================
    # ADDITIONAL UTILITY COMMANDS
    # ========================================
    
    # metrics and reporting
    metrics_parser = subparsers.add_parser("metrics", help="Metrics and reporting")
    metrics_sub = metrics_parser.add_subparsers(dest="metrics_cmd")
    
    metrics_show = metrics_sub.add_parser("show", help="Show system metrics")
    metrics_show.add_argument("--type", choices=["incidents", "problems", "changes", "availability", "performance"], help="Metric type")
    metrics_show.add_argument("--period", choices=["day", "week", "month", "quarter"], default="month", help="Time period")
    metrics_show.add_argument("--json", action="store_true")
    metrics_show.set_defaults(func=cmd_metrics_show)
    
    # knowledge management
    knowledge_parser = subparsers.add_parser("knowledge", help="Knowledge Management System")
    knowledge_sub = knowledge_parser.add_subparsers(dest="knowledge_cmd")
    
    kb_create = knowledge_sub.add_parser("create", help="Create knowledge article")
    kb_create.add_argument("--title", required=True, help="Article title")
    kb_create.add_argument("--content", required=True, help="Article content")
    kb_create.add_argument("--category", help="Article category")
    kb_create.add_argument("--tags", nargs="+", help="Article tags")
    kb_create.add_argument("--json", action="store_true")
    kb_create.set_defaults(func=cmd_knowledge_create)
    
    kb_search = knowledge_sub.add_parser("search", help="Search knowledge articles")
    kb_search.add_argument("query", help="Search query")
    kb_search.add_argument("--limit", type=int, default=10, help="Max results")
    kb_search.add_argument("--json", action="store_true")
    kb_search.set_defaults(func=cmd_knowledge_search)
    
    # service catalog
    catalog_parser = subparsers.add_parser("catalog", help="Service Catalog management")
    catalog_sub = catalog_parser.add_subparsers(dest="catalog_cmd")
    
    cat_list = catalog_sub.add_parser("list", help="List service catalog items")
    cat_list.add_argument("--category", help="Filter by category")
    cat_list.add_argument("--json", action="store_true")
    cat_list.set_defaults(func=cmd_catalog_list)
    
    cat_add = catalog_sub.add_parser("add", help="Add service catalog item")
    cat_add.add_argument("--name", required=True, help="Service name")
    cat_add.add_argument("--description", help="Service description")
    cat_add.add_argument("--category", help="Service category")
    cat_add.add_argument("--price", type=float, help="Service price")
    cat_add.add_argument("--json", action="store_true")
    cat_add.set_defaults(func=cmd_catalog_add)
    
    # workflow management
    workflow_parser = subparsers.add_parser("workflow", help="Workflow management")
    workflow_sub = workflow_parser.add_subparsers(dest="workflow_cmd")
    
    wf_list = workflow_sub.add_parser("list", help="List workflows")
    wf_list.add_argument("--status", help="Filter by status")
    wf_list.add_argument("--json", action="store_true")
    wf_list.set_defaults(func=cmd_workflow_list)
    
    wf_execute = workflow_sub.add_parser("execute", help="Execute workflow")
    wf_execute.add_argument("workflow_id", help="Workflow ID")
    wf_execute.add_argument("--params", help="Workflow parameters as JSON")
    wf_execute.add_argument("--json", action="store_true")
    wf_execute.set_defaults(func=cmd_workflow_execute)
    
    # configuration management
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_sub = config_parser.add_subparsers(dest="config_cmd")
    
    config_show = config_sub.add_parser("show", help="Show configuration")
    config_show.add_argument("--section", help="Configuration section")
    config_show.add_argument("--json", action="store_true")
    config_show.set_defaults(func=cmd_config_show)
    
    config_set = config_sub.add_parser("set", help="Set configuration value")
    config_set.add_argument("key", help="Configuration key")
    config_set.add_argument("value", help="Configuration value")
    config_set.add_argument("--json", action="store_true")
    config_set.set_defaults(func=cmd_config_set)
    
    # testing and validation
    test_parser = subparsers.add_parser("test", help="Testing and validation")
    test_sub = test_parser.add_subparsers(dest="test_cmd")
    
    test_run = test_sub.add_parser("run", help="Run tests")
    test_run.add_argument("--suite", help="Test suite to run")
    test_run.add_argument("--verbose", action="store_true", help="Verbose output")
    test_run.add_argument("--json", action="store_true")
    test_run.set_defaults(func=cmd_test_run)
    
    test_validate = test_sub.add_parser("validate", help="Validate system")
    test_validate.add_argument("--component", help="Component to validate")
    test_validate.add_argument("--json", action="store_true")
    test_validate.set_defaults(func=cmd_test_validate)
    
    # import/export
    import_parser = subparsers.add_parser("import", help="Import data")
    import_parser.add_argument("file_path", help="File to import")
    import_parser.add_argument("--type", choices=["csv", "json", "xml"], help="File format")
    import_parser.add_argument("--entity", choices=["incidents", "problems", "changes", "cis"], help="Entity type")
    import_parser.add_argument("--dry-run", action="store_true", help="Dry run (don't actually import)")
    import_parser.add_argument("--json", action="store_true")
    import_parser.set_defaults(func=cmd_import_data)
    
    export_parser = subparsers.add_parser("export", help="Export data")
    export_parser.add_argument("--entity", required=True, choices=["incidents", "problems", "changes", "cis"], help="Entity type")
    export_parser.add_argument("--format", choices=["csv", "json", "xml"], default="json", help="Export format")
    export_parser.add_argument("--output", help="Output file path")
    export_parser.add_argument("--filter", help="Filter criteria as JSON")
    export_parser.add_argument("--json", action="store_true")
    export_parser.set_defaults(func=cmd_export_data)

    # Parse arguments and execute
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        return
        
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        if os.getenv("DEBUG"):
            import traceback
            traceback.print_exc()
        sys.exit(1)


# ========================================
# ADDITIONAL COMMAND IMPLEMENTATIONS
# ========================================

def cmd_metrics_show(args: argparse.Namespace) -> None:
    """Show system metrics"""
    try:
        o = ensure_orch()
        
        metrics = {}
        if args.type == "incidents" or not args.type:
            incidents = json_store.query("incidents")
            metrics["incidents"] = {
                "total": len(incidents),
                "open": len([i for i in incidents if i.get("state") in ["new", "in_progress"]]),
                "closed": len([i for i in incidents if i.get("state") == "closed"]),
                "high_priority": len([i for i in incidents if i.get("priority") in ["high", "critical"]])
            }
        
        if args.type == "problems" or not args.type:
            problems = json_store.query("problems")
            metrics["problems"] = {
                "total": len(problems),
                "open": len([p for p in problems if p.get("state") in ["new", "in_progress"]]),
                "closed": len([p for p in problems if p.get("state") == "closed"])
            }
        
        if args.type == "changes" or not args.type:
            changes = json_store.query("changes")
            metrics["changes"] = {
                "total": len(changes),
                "pending": len([c for c in changes if c.get("state") == "pending"]),
                "approved": len([c for c in changes if c.get("state") == "approved"]),
                "implemented": len([c for c in changes if c.get("state") == "implemented"])
            }
        
        if args.type == "availability" or not args.type:
            dash = o.build_integrated_dashboard()
            metrics["availability"] = dash.get("service_level", {})
        
        if args.json:
            print_json(metrics)
        else:
            print(f"System Metrics ({args.period}):")
            for category, data in metrics.items():
                print(f"\n{category.title()}:")
                for key, value in data.items():
                    print(f"  {key.replace('_', ' ').title()}: {value}")
                    
    except Exception as e:
        print(f"✗ Failed to show metrics: {e}")


def cmd_knowledge_create(args: argparse.Namespace) -> None:
    """Create knowledge article"""
    try:
        article = {
            "id": f"KB{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": args.title,
            "content": args.content,
            "category": args.category or "General",
            "tags": args.tags or [],
            "created": datetime.datetime.now().isoformat(),
            "created_by": "cli_user",
            "status": "published"
        }
        
        articles = json_store.query("knowledge_articles")
        articles.append(article)
        json_store.save("knowledge_articles", articles)
        
        result = {"article_id": article["id"], "created": True}
        
        if args.json:
            print_json(result)
        else:
            print(f"✓ Created knowledge article: {article['id']}")
            
    except Exception as e:
        print(f"✗ Failed to create knowledge article: {e}")


def cmd_knowledge_search(args: argparse.Namespace) -> None:
    """Search knowledge articles"""
    try:
        articles = json_store.query("knowledge_articles")
        
        # Simple text search
        query_lower = args.query.lower()
        matches = []
        for article in articles:
            if (query_lower in article.get("title", "").lower() or 
                query_lower in article.get("content", "").lower() or
                query_lower in " ".join(article.get("tags", [])).lower()):
                matches.append(article)
        
        result = {"total": len(matches), "articles": matches[:args.limit]}
        
        if args.json:
            print_json(result)
        else:
            if not matches:
                print(f"No articles found for query: {args.query}")
                return
                
            print(f"Found {len(matches)} articles:")
            for article in matches[:args.limit]:
                print(f"  • {article.get('id')}: {article.get('title')}")
                print(f"    Category: {article.get('category')}")
                print(f"    Tags: {', '.join(article.get('tags', []))}")
                
    except Exception as e:
        print(f"✗ Failed to search knowledge articles: {e}")


def cmd_catalog_list(args: argparse.Namespace) -> None:
    """List service catalog items"""
    try:
        items = json_store.query("service_catalog")
        
        if args.category:
            items = [item for item in items if item.get("category") == args.category]
        
        result = {"total": len(items), "services": items}
        
        if args.json:
            print_json(result)
        else:
            if not items:
                print("No service catalog items found")
                return
                
            headers = ["Name", "Category", "Price", "Status"]
            table_data = []
            for item in items:
                table_data.append({
                    "Name": item.get("name", "N/A"),
                    "Category": item.get("category", "N/A"),
                    "Price": f"${item.get('price', 0):.2f}" if item.get("price") else "Free",
                    "Status": item.get("status", "Active")
                })
            print_table(table_data, headers)
            
    except Exception as e:
        print(f"✗ Failed to list catalog items: {e}")


def cmd_catalog_add(args: argparse.Namespace) -> None:
    """Add service catalog item"""
    try:
        item = {
            "id": f"SVC{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": args.name,
            "description": args.description or args.name,
            "category": args.category or "General",
            "price": args.price or 0.0,
            "status": "Active",
            "created": datetime.datetime.now().isoformat()
        }
        
        items = json_store.query("service_catalog")
        items.append(item)
        json_store.save("service_catalog", items)
        
        result = {"service_id": item["id"], "created": True}
        
        if args.json:
            print_json(result)
        else:
            print(f"✓ Added service catalog item: {item['name']} ({item['id']})")
            
    except Exception as e:
        print(f"✗ Failed to add catalog item: {e}")


def cmd_workflow_list(args: argparse.Namespace) -> None:
    """List workflows"""
    try:
        workflows = [
            {"id": "WF001", "name": "Incident Resolution", "status": "active", "type": "incident"},
            {"id": "WF002", "name": "Change Approval", "status": "active", "type": "change"},
            {"id": "WF003", "name": "Problem Investigation", "status": "active", "type": "problem"},
            {"id": "WF004", "name": "Service Request Fulfillment", "status": "active", "type": "service_request"}
        ]
        
        if args.status:
            workflows = [wf for wf in workflows if wf.get("status") == args.status]
        
        result = {"total": len(workflows), "workflows": workflows}
        
        if args.json:
            print_json(result)
        else:
            headers = ["ID", "Name", "Type", "Status"]
            table_data = []
            for wf in workflows:
                table_data.append({
                    "ID": wf["id"],
                    "Name": wf["name"],
                    "Type": wf["type"],
                    "Status": wf["status"]
                })
            print_table(table_data, headers)
            
    except Exception as e:
        print(f"✗ Failed to list workflows: {e}")


def cmd_workflow_execute(args: argparse.Namespace) -> None:
    """Execute workflow"""
    try:
        params = json.loads(args.params) if args.params else {}
        
        execution = {
            "execution_id": f"EXE{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "workflow_id": args.workflow_id,
            "parameters": params,
            "status": "completed",
            "started": datetime.datetime.now().isoformat(),
            "completed": datetime.datetime.now().isoformat()
        }
        
        result = {"execution": execution}
        
        if args.json:
            print_json(result)
        else:
            print(f"✓ Executed workflow: {args.workflow_id}")
            print(f"  Execution ID: {execution['execution_id']}")
            print(f"  Status: {execution['status']}")
            
    except Exception as e:
        print(f"✗ Failed to execute workflow: {e}")


def cmd_config_show(args: argparse.Namespace) -> None:
    """Show configuration"""
    try:
        config_file = Path("config/reasonops.json")
        
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
        else:
            config = {"message": "No configuration file found"}
        
        if args.section:
            config = config.get(args.section, {})
        
        if args.json:
            print_json(config)
        else:
            print("Configuration:")
            for key, value in config.items():
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"✗ Failed to show configuration: {e}")


def cmd_config_set(args: argparse.Namespace) -> None:
    """Set configuration value"""
    try:
        config_file = Path("config/reasonops.json")
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
        else:
            config = {}
        
        # Simple key-value setting (could be enhanced for nested keys)
        config[args.key] = args.value
        
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        result = {"key": args.key, "value": args.value, "updated": True}
        
        if args.json:
            print_json(result)
        else:
            print(f"✓ Set configuration: {args.key} = {args.value}")
            
    except Exception as e:
        print(f"✗ Failed to set configuration: {e}")


def cmd_test_run(args: argparse.Namespace) -> None:
    """Run tests"""
    try:
        import subprocess
        
        if args.suite:
            test_command = ["python", "-m", "pytest", f"tests/test_{args.suite}.py"]
        else:
            test_command = ["python", "-m", "pytest", "tests/"]
        
        if args.verbose:
            test_command.append("-v")
        
        result = subprocess.run(test_command, capture_output=True, text=True)
        
        test_result = {
            "command": " ".join(test_command),
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
        
        if args.json:
            print_json(test_result)
        else:
            print(f"Test Results:")
            print(f"  Command: {test_result['command']}")
            print(f"  Success: {'✓' if test_result['success'] else '✗'}")
            print(f"  Output:\n{result.stdout}")
            if result.stderr:
                print(f"  Errors:\n{result.stderr}")
                
    except Exception as e:
        print(f"✗ Failed to run tests: {e}")


def cmd_test_validate(args: argparse.Namespace) -> None:
    """Validate system"""
    try:
        validations = []
        
        # Storage validation
        data_dir = Path("storage/data")
        validations.append({
            "component": "storage",
            "check": "data_directory_exists",
            "status": "pass" if data_dir.exists() else "fail",
            "message": f"Data directory {'exists' if data_dir.exists() else 'missing'}"
        })
        
        # Configuration validation
        config_file = Path("config/reasonops.json")
        validations.append({
            "component": "configuration",
            "check": "config_file_exists",
            "status": "pass" if config_file.exists() else "fail",
            "message": f"Config file {'exists' if config_file.exists() else 'missing'}"
        })
        
        # Orchestrator validation
        try:
            o = ensure_orch()
            validations.append({
                "component": "orchestrator",
                "check": "initialization",
                "status": "pass",
                "message": "Orchestrator can be initialized"
            })
        except Exception as e:
            validations.append({
                "component": "orchestrator",
                "check": "initialization",
                "status": "fail",
                "message": f"Orchestrator error: {e}"
            })
        
        if args.component:
            validations = [v for v in validations if v["component"] == args.component]
        
        result = {
            "total_checks": len(validations),
            "passed": len([v for v in validations if v["status"] == "pass"]),
            "failed": len([v for v in validations if v["status"] == "fail"]),
            "validations": validations
        }
        
        if args.json:
            print_json(result)
        else:
            print(f"System Validation Results:")
            print(f"  Total checks: {result['total_checks']}")
            print(f"  Passed: {result['passed']}")
            print(f"  Failed: {result['failed']}")
            print("\nDetailed Results:")
            for validation in validations:
                status_icon = "✓" if validation["status"] == "pass" else "✗"
                print(f"  {status_icon} {validation['component']}.{validation['check']}: {validation['message']}")
                
    except Exception as e:
        print(f"✗ Failed to validate system: {e}")


def cmd_import_data(args: argparse.Namespace) -> None:
    """Import data"""
    try:
        file_path = Path(args.file_path)
        
        if not file_path.exists():
            print(f"✗ File not found: {file_path}")
            return
        
        # Determine file format
        file_format = args.type or file_path.suffix[1:].lower()
        
        imported_count = 0
        if file_format == "json":
            with open(file_path, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                imported_count = len(data)
                if not args.dry_run:
                    json_store.save(args.entity or "imported_data", data)
        elif file_format == "csv":
            import csv
            with open(file_path, "r") as f:
                reader = csv.DictReader(f)
                data = list(reader)
                imported_count = len(data)
                if not args.dry_run:
                    json_store.save(args.entity or "imported_data", data)
        
        result = {
            "file": str(file_path),
            "format": file_format,
            "entity": args.entity,
            "records": imported_count,
            "dry_run": args.dry_run,
            "imported": not args.dry_run
        }
        
        if args.json:
            print_json(result)
        else:
            action = "Would import" if args.dry_run else "Imported"
            print(f"✓ {action} {imported_count} records from {file_path}")
            
    except Exception as e:
        print(f"✗ Failed to import data: {e}")


def cmd_export_data(args: argparse.Namespace) -> None:
    """Export data"""
    try:
        # Get data
        data = json_store.query(args.entity)
        
        # Apply filter if provided
        if args.filter:
            filter_criteria = json.loads(args.filter)
            # Simple filtering (could be enhanced)
            filtered_data = []
            for item in data:
                match = True
                for key, value in filter_criteria.items():
                    if item.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_data.append(item)
            data = filtered_data
        
        # Determine output path
        output_path = Path(args.output) if args.output else Path(f"exports/{args.entity}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{args.format}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export data
        if args.format == "json":
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        elif args.format == "csv":
            if data:
                import csv
                with open(output_path, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        
        result = {
            "entity": args.entity,
            "format": args.format,
            "records": len(data),
            "output": str(output_path)
        }
        
        if args.json:
            print_json(result)
        else:
            print(f"✓ Exported {len(data)} {args.entity} records to {output_path}")
            
    except Exception as e:
        print(f"✗ Failed to export data: {e}")


# ========================================
# Agent Command Implementations
# ========================================

def cmd_agents_run(args: argparse.Namespace) -> None:
    """Execute AI agent orchestration"""
    import asyncio
    
    try:
        event_data = json.loads(args.event_data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in --event-data: {e}", file=sys.stderr)
        sys.exit(1)
    
    config = {}
    orchestrator = CollaborativeAgentsOrchestrator(base_provider_config=None)
    
    async def run():
        result = await orchestrator.handle_event(
            event_type=args.event_type,
            event_data=event_data
        )
        return result
    
    result = asyncio.run(run())
    
    if args.json:
        print_json(result)
    else:
        print(f"✓ Agent orchestration completed for event: {args.event_type}")
        print(f"  Decisions: {len(result.get('decisions', []))}")
        print(f"  Actions: {len(result.get('actions', []))}")


def cmd_agents_list_decisions(args: argparse.Namespace) -> None:
    """List agent decision history"""
    decisions = json_store.get_agent_decisions(
        limit=args.limit,
        event_type=args.event_type,
        agent_name=args.agent_name
    )
    
    result = {"total": len(decisions), "decisions": decisions}
    
    if args.json:
        print_json(result)
    else:
        print(f"Found {len(decisions)} agent decisions:")
        for idx, dec in enumerate(decisions[:10], 1):
            print(f"  {idx}. {dec.get('agent_name', 'unknown')} @ {dec.get('timestamp', 'N/A')}")
            print(f"     Event: {dec.get('event_type', 'N/A')}")
            print(f"     Decision: {dec.get('decision', 'N/A')[:80]}...")
        if len(decisions) > 10:
            print(f"  ... and {len(decisions) - 10} more")


def cmd_agents_configure_llm(args: argparse.Namespace) -> None:
    """Configure LLM provider"""
    from ai_agents.multi_llm_provider import LLMConfig, LLMProvider, ModelType, MultiLLMManager
    
    provider_map = {
        "ollama": LLMProvider.OLLAMA,
        "openai": LLMProvider.OPENAI,
        "anthropic": LLMProvider.ANTHROPIC,
        "google": LLMProvider.GOOGLE,
        "azure": LLMProvider.AZURE_OPENAI,
        "huggingface": LLMProvider.HUGGINGFACE,
        "mock": LLMProvider.MOCK
    }
    
    provider_enum = provider_map.get(args.provider.lower())
    if not provider_enum:
        print(f"Error: Unknown provider '{args.provider}'. Valid: {list(provider_map.keys())}", file=sys.stderr)
        sys.exit(1)
    
    # Set model based on provider if not specified
    if not args.model:
        if provider_enum == LLMProvider.OLLAMA:
            args.model = "deepseek-coder"  # Use available model
        elif provider_enum == LLMProvider.OPENAI:
            args.model = "gpt-4"
        else:
            args.model = "default"
    
    llm_config = LLMConfig(
        provider=provider_enum,
        model=ModelType.CUSTOM if args.model == "deepseek-coder" else ModelType.LLAMA_2_7B,
        api_key=args.api_key,
        temperature=args.temperature,
        api_base="http://localhost:11434" if provider_enum == LLMProvider.OLLAMA else None,
        timeout=30
    )
    
    # Test the configuration by creating a manager and adding the provider
    try:
        manager = MultiLLMManager()
        manager.add_provider("test_provider", llm_config)
        manager.set_primary_provider("test_provider")
        
        result = {
            "status": "success",
            "provider": args.provider,
            "model": args.model,
            "temperature": args.temperature,
            "message": f"LLM provider configured: {args.provider}"
        }
        
        if args.json:
            print_json(result)
        else:
            print(f"✓ {result['message']}")
            print(f"  Model: {result['model']}")
            print(f"  Temperature: {result['temperature']}")
            if provider_enum == LLMProvider.OLLAMA:
                print(f"  Endpoint: http://localhost:11434")
                
    except Exception as e:
        result = {
            "status": "error",
            "provider": args.provider,
            "model": args.model,
            "error": str(e),
            "message": f"Failed to configure provider: {e}"
        }
        
        if args.json:
            print_json(result)
        else:
            print(f"✗ {result['message']}")
        sys.exit(1)


def cmd_agents_health(args: argparse.Namespace) -> None:
    """Check LLM provider health"""
    import asyncio
    import time
    from ai_agents.multi_llm_provider import LLMConfig, LLMProvider, ModelType, MultiLLMManager
    
    async def check_providers():
        """Check health of available providers"""
        manager = MultiLLMManager()
        
        # Add available providers for testing
        providers_to_test = [
            ("ollama", LLMProvider.OLLAMA, "deepseek-coder", "http://localhost:11434"),
            ("mock", LLMProvider.MOCK, "default", None)
        ]
        
        health_results = {}
        
        for name, provider_type, model, api_base in providers_to_test:
            try:
                config = LLMConfig(
                    provider=provider_type,
                    model=ModelType.CUSTOM if model == "deepseek-coder" else ModelType.LLAMA_2_7B,
                    api_base=api_base,
                    timeout=10  # Shorter timeout for health checks
                )
                
                start_time = time.time()
                manager.add_provider(name, config)
                
                # Test with a simple prompt
                test_response = await manager.generate_response(
                    "Hello, respond with 'OK' if you're working.",
                    provider_name=name
                )
                
                end_time = time.time()
                latency = (end_time - start_time) * 1000  # Convert to ms
                
                if test_response and test_response.content:
                    health_results[name] = {
                        "status": "healthy",
                        "latency_ms": round(latency, 2),
                        "provider": provider_type.value,
                        "model": model,
                        "message": "Provider responding normally"
                    }
                else:
                    health_results[name] = {
                        "status": "degraded",
                        "provider": provider_type.value,
                        "model": model,
                        "message": "Provider not responding properly"
                    }
                    
            except Exception as e:
                health_results[name] = {
                    "status": "unhealthy",
                    "provider": provider_type.value if provider_type else "unknown",
                    "model": model,
                    "error": str(e),
                    "message": f"Provider failed: {str(e)}"
                }
        
        return health_results
    
    try:
        health_summary = asyncio.run(check_providers())
        
        result = {
            "status": "ok",
            "timestamp": datetime.datetime.now().isoformat(),
            "providers": health_summary,
            "total_providers": len(health_summary),
            "healthy_providers": len([p for p in health_summary.values() if p["status"] == "healthy"])
        }
        
        if args.json:
            print_json(result)
        else:
            print("🏥 LLM Provider Health Check")
            print(f"Timestamp: {result['timestamp']}")
            print(f"Total Providers: {result['total_providers']}")
            print(f"Healthy Providers: {result['healthy_providers']}")
            print()
            
            for provider_name, health in health_summary.items():
                status_icon = "✅" if health["status"] == "healthy" else "⚠️" if health["status"] == "degraded" else "❌"
                print(f"{status_icon} {provider_name.upper()}: {health['status']}")
                print(f"   Provider: {health['provider']}")
                print(f"   Model: {health['model']}")
                if health.get("latency_ms"):
                    print(f"   Latency: {health['latency_ms']:.0f}ms")
                print(f"   Message: {health['message']}")
                print()
                
    except Exception as e:
        result = {
            "status": "error",
            "error": str(e),
            "message": f"Health check failed: {e}"
        }
        
        if args.json:
            print_json(result)
        else:
            print(f"❌ Health check failed: {e}")
        sys.exit(1)


def cmd_agents_list_providers(args: argparse.Namespace) -> None:
    """List available LLM providers"""
    from ai_agents.multi_llm_provider import LLMProvider, ModelType
    
    result = {
        "providers": [p.value for p in LLMProvider],
        "models": {
            "ollama": ["llama2-7b", "mistral-7b", "codellama", "llama2-13b"],
            "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "google": ["gemini-pro", "gemini-pro-vision"],
            "azure": ["gpt-4", "gpt-35-turbo"],
            "huggingface": ["custom models via API"],
            "mock": ["mock-model"]
        },
        "recommended": {
            "local": "ollama + llama2-7b",
            "cloud": "openai + gpt-4-turbo",
            "enterprise": "azure + gpt-4"
        }
    }
    
    if args.json:
        print_json(result)
    else:
        print("Available LLM Providers:")
        for provider in result["providers"]:
            models = result["models"].get(provider, [])
            print(f"  • {provider}")
            print(f"    Models: {', '.join(models[:3])}")
        print("\nRecommended Configurations:")
        for use_case, config in result["recommended"].items():
            print(f"  • {use_case}: {config}")


# ========================================
# SYSTEM COMMAND IMPLEMENTATIONS
# ========================================

def cmd_system_status(args: argparse.Namespace) -> None:
    """Show system status and health"""
    status = {
        "framework": {
            "name": FRAMEWORK_NAME,
            "version": FRAMEWORK_VERSION,
            "status": "running"
        },
        "components": {
            "storage": _check_storage_health(),
            "orchestrator": _check_orchestrator_health(),
            "agents": _check_agents_health()
        },
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    if args.json:
        print_json(status)
    else:
        print(f"🚀 {FRAMEWORK_NAME} v{FRAMEWORK_VERSION}")
        print(f"Status: {status['framework']['status']}")
        print("\nComponent Health:")
        for comp, health in status["components"].items():
            icon = "✓" if health["status"] == "healthy" else "⚠" if health["status"] == "degraded" else "✗"
            print(f"  {icon} {comp}: {health['status']}")


def cmd_system_init(args: argparse.Namespace) -> None:
    """Initialize ReasonOps workspace"""
    workspace_path = Path(args.path).resolve()
    
    if workspace_path.exists() and any(workspace_path.iterdir()) and not args.force:
        print(f"✗ Directory {workspace_path} is not empty. Use --force to initialize anyway.")
        return
    
    # Create directory structure
    dirs_to_create = [
        "config",
        "data",
        "logs",
        "exports",
        "backups"
    ]
    
    for dir_name in dirs_to_create:
        dir_path = workspace_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")
    
    # Create config files
    config_data = {
        "framework": {
            "name": FRAMEWORK_NAME,
            "version": FRAMEWORK_VERSION,
            "initialized": datetime.datetime.now().isoformat()
        },
        "storage": {
            "data_dir": str(workspace_path / "data"),
            "log_dir": str(workspace_path / "logs")
        }
    }
    
    config_file = workspace_path / "config" / "reasonops.json"
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)
    print(f"✓ Created config file: {config_file}")
    
    print(f"\n🎉 ReasonOps workspace initialized at {workspace_path}")


# ========================================
# INCIDENT MANAGEMENT COMMANDS
# ========================================

def cmd_incident_create(args: argparse.Namespace) -> None:
    """Create new incident"""
    try:
        from practices.incident_management import IncidentManagement, IncidentCategory
        from core.service_value_system import Person, Impact, Urgency
        
        incident_mgmt = IncidentManagement()
        
        # Map string values to enums
        impact_map = {"low": Impact.LOW, "medium": Impact.MEDIUM, "high": Impact.HIGH, "critical": Impact.HIGH}
        urgency_map = {"low": Urgency.LOW, "medium": Urgency.MEDIUM, "high": Urgency.HIGH, "critical": Urgency.HIGH}
        
        impact = impact_map.get(args.impact, Impact.MEDIUM) if args.impact else Impact.MEDIUM
        urgency = urgency_map.get(args.urgency, Urgency.MEDIUM) if args.urgency else Urgency.MEDIUM
        
        # Create caller - use provided or default
        if args.caller:
            caller = Person("user1", args.caller, args.caller, "End User", "IT")
        else:
            caller = Person("system", "System", "system@company.com", "System", "IT")
        
        # Map category string to enum
        category_map = {
            "hardware": IncidentCategory.HARDWARE,
            "software": IncidentCategory.SOFTWARE,
            "network": IncidentCategory.NETWORK,
            "security": IncidentCategory.SECURITY,
            "service": IncidentCategory.SERVICE,
            "infrastructure": IncidentCategory.INFRASTRUCTURE,
            "application": IncidentCategory.APPLICATION,
            "database": IncidentCategory.DATABASE,
            "performance": IncidentCategory.APPLICATION  # Map performance to application
        }
        
        category = category_map.get(args.category.lower() if args.category else "service", IncidentCategory.SERVICE)
        
        incident = incident_mgmt.create_incident(
            short_description=args.title,
            description=args.description or args.title,
            caller=caller,
            category=category,
            impact=impact,
            urgency=urgency
        )
        
        result = {
            "incident_id": incident.number,
            "title": incident.short_description,
            "status": incident.state.value,
            "priority": incident.priority.value,
            "created": incident.opened_at.isoformat()
        }
        
        if args.json:
            print_json(result)
        else:
            print(f"✓ Created incident: {incident.number}")
            print(f"  Title: {incident.short_description}")
            print(f"  Priority: {incident.priority.value}")
            print(f"  Status: {incident.state.value}")
            
    except Exception as e:
        import traceback
        print(f"✗ Failed to create incident: {e}")
        if hasattr(args, 'debug') and args.debug:
            traceback.print_exc()


def cmd_incident_list(args: argparse.Namespace) -> None:
    """List incidents"""
    try:
        # Get incidents from storage
        incidents = json_store.query("incidents", limit=args.limit)
        
        if args.status:
            incidents = [inc for inc in incidents if inc.get("status") == args.status]
        if args.priority:
            incidents = [inc for inc in incidents if inc.get("priority") == args.priority]
        
        result = {
            "total": len(incidents),
            "incidents": incidents[:args.limit]
        }
        
        if args.json:
            print_json(result)
        else:
            if not incidents:
                print("No incidents found")
                return
                
            headers = ["ID", "Title", "Status", "Priority", "Created"]
            table_data = []
            for inc in incidents[:args.limit]:
                table_data.append({
                    "ID": inc.get("number", "N/A"),
                    "Title": inc.get("short_description", "N/A")[:40] + ("..." if len(inc.get("short_description", "")) > 40 else ""),
                    "Status": inc.get("state", "N/A"),
                    "Priority": inc.get("priority", "N/A"),
                    "Created": inc.get("opened_at", "N/A")[:10] if inc.get("opened_at") else "N/A"
                })
            print_table(table_data, headers)
            
    except Exception as e:
        print(f"✗ Failed to list incidents: {e}")


def cmd_incident_show(args: argparse.Namespace) -> None:
    """Show incident details"""
    try:
        incidents = json_store.query("incidents")
        incident = next((inc for inc in incidents if inc.get("number") == args.incident_id), None)
        
        if not incident:
            print(f"✗ Incident {args.incident_id} not found")
            return
        
        if args.json:
            print_json(incident)
        else:
            print(f"Incident: {incident.get('number', 'N/A')}")
            print(f"Title: {incident.get('short_description', 'N/A')}")
            print(f"Description: {incident.get('description', 'N/A')}")
            print(f"Status: {incident.get('state', 'N/A')}")
            print(f"Priority: {incident.get('priority', 'N/A')}")
            print(f"Created: {incident.get('opened_at', 'N/A')}")
            print(f"Updated: {incident.get('sys_updated_on', 'N/A')}")
            
    except Exception as e:
        print(f"✗ Failed to show incident: {e}")


def cmd_incident_update(args: argparse.Namespace) -> None:
    """Update incident"""
    try:
        incidents = json_store.query("incidents")
        incident_idx = None
        incident = None
        
        for i, inc in enumerate(incidents):
            if inc.get("number") == args.incident_id:
                incident_idx = i
                incident = inc
                break
        
        if not incident:
            print(f"✗ Incident {args.incident_id} not found")
            return
        
        # Update fields
        if args.status:
            incident["state"] = args.status
        if args.priority:
            incident["priority"] = args.priority
        if args.assignee:
            incident["assigned_to"] = args.assignee
        if args.comment:
            if "work_notes" not in incident:
                incident["work_notes"] = []
            incident["work_notes"].append({
                "timestamp": datetime.datetime.now().isoformat(),
                "comment": args.comment
            })
        
        incident["sys_updated_on"] = datetime.datetime.now().isoformat()
        
        # Save back to storage
        incidents[incident_idx] = incident
        json_store.save("incidents", incidents)
        
        result = {"incident_id": args.incident_id, "updated": True}
        
        if args.json:
            print_json(result)
        else:
            print(f"✓ Updated incident: {args.incident_id}")
            
    except Exception as e:
        print(f"✗ Failed to update incident: {e}")


# ========================================
# PROBLEM MANAGEMENT COMMANDS
# ========================================

def cmd_problem_create(args: argparse.Namespace) -> None:
    """Create new problem"""
    try:
        from practices.problem_management import ProblemManagement
        
        problem_mgmt = ProblemManagement()
        
        problem = problem_mgmt.create_problem(
            short_description=args.title,
            description=args.description or args.title
        )
        
        result = {
            "problem_id": problem.number,
            "title": problem.short_description,
            "status": problem.state.value,
            "created": problem.opened_at.isoformat()
        }
        
        if args.json:
            print_json(result)
        else:
            print(f"✓ Created problem: {problem.number}")
            
    except Exception as e:
        print(f"✗ Failed to create problem: {e}")


def cmd_problem_list(args: argparse.Namespace) -> None:
    """List problems"""
    try:
        problems = json_store.query("problems", limit=args.limit)
        
        if args.status:
            problems = [prob for prob in problems if prob.get("status") == args.status]
        
        result = {"total": len(problems), "problems": problems}
        
        if args.json:
            print_json(result)
        else:
            if not problems:
                print("No problems found")
                return
                
            headers = ["ID", "Title", "Status", "Created"]
            table_data = []
            for prob in problems:
                table_data.append({
                    "ID": prob.get("number", "N/A"),
                    "Title": prob.get("short_description", "N/A")[:50] + ("..." if len(prob.get("short_description", "")) > 50 else ""),
                    "Status": prob.get("state", "N/A"),
                    "Created": prob.get("opened_at", "N/A")[:10] if prob.get("opened_at") else "N/A"
                })
            print_table(table_data, headers)
            
    except Exception as e:
        print(f"✗ Failed to list problems: {e}")


# ========================================
# CHANGE MANAGEMENT COMMANDS  
# ========================================

def cmd_change_create(args: argparse.Namespace) -> None:
    """Create new change"""
    try:
        from practices.change_enablement import ChangeEnablement, ChangeType, RiskLevel
        
        change_mgmt = ChangeEnablement()
        
        # Map string values to enums
        type_map = {"normal": ChangeType.NORMAL, "standard": ChangeType.STANDARD, "emergency": ChangeType.EMERGENCY}
        risk_map = {"low": RiskLevel.LOW, "medium": RiskLevel.MEDIUM, "high": RiskLevel.HIGH}
        
        change_type = type_map.get(args.type, ChangeType.NORMAL)
        risk_level = risk_map.get(args.risk, RiskLevel.MEDIUM)
        
        change = change_mgmt.create_change_request(
            short_description=args.title,
            description=args.description or args.title,
            change_type=change_type,
            risk_level=risk_level
        )
        
        result = {
            "change_id": change.number,
            "title": change.short_description,
            "type": change.change_type.value,
            "risk": change.risk_level.value,
            "status": change.state.value,
            "created": change.opened_at.isoformat()
        }
        
        if args.json:
            print_json(result)
        else:
            print(f"✓ Created change: {change.number}")
            
    except Exception as e:
        print(f"✗ Failed to create change: {e}")


def cmd_change_list(args: argparse.Namespace) -> None:
    """List changes"""
    try:
        changes = json_store.query("changes", limit=args.limit)
        
        if args.status:
            changes = [chg for chg in changes if chg.get("status") == args.status]
        if args.type:
            changes = [chg for chg in changes if chg.get("type") == args.type]
        
        result = {"total": len(changes), "changes": changes}
        
        if args.json:
            print_json(result)
        else:
            if not changes:
                print("No changes found")
                return
                
            headers = ["ID", "Title", "Type", "Risk", "Status", "Created"]
            table_data = []
            for chg in changes:
                table_data.append({
                    "ID": chg.get("number", "N/A"),
                    "Title": chg.get("short_description", "N/A")[:40] + ("..." if len(chg.get("short_description", "")) > 40 else ""),
                    "Type": chg.get("change_type", "N/A"),
                    "Risk": chg.get("risk_level", "N/A"),
                    "Status": chg.get("state", "N/A"),
                    "Created": chg.get("opened_at", "N/A")[:10] if chg.get("opened_at") else "N/A"
                })
            print_table(table_data, headers)
            
    except Exception as e:
        print(f"✗ Failed to list changes: {e}")


# ========================================
# CMDB COMMANDS
# ========================================

def cmd_cmdb_add(args: argparse.Namespace) -> None:
    """Add configuration item"""
    try:
        from core.service_value_system import ConfigurationItem
        
        ci = ConfigurationItem(
            name=args.name,
            ci_type=args.type,
            ci_class=args.ci_class or args.type,
            status=args.status,
            location=args.location,
            owner=args.owner
        )
        
        # Store CI
        ci_data = {
            "sys_id": ci.sys_id,
            "name": ci.name,
            "type": ci.ci_type,
            "class": ci.ci_class,
            "status": ci.status,
            "location": ci.location,
            "owner": ci.owner,
            "created": datetime.datetime.now().isoformat()
        }
        
        cis = json_store.query("configuration_items")
        cis.append(ci_data)
        json_store.save("configuration_items", cis)
        
        result = {"ci_id": ci.sys_id, "name": ci.name, "created": True}
        
        if args.json:
            print_json(result)
        else:
            print(f"✓ Added CI: {ci.name} ({ci.sys_id})")
            
    except Exception as e:
        print(f"✗ Failed to add CI: {e}")


def cmd_cmdb_list(args: argparse.Namespace) -> None:
    """List configuration items"""
    try:
        cis = json_store.query("configuration_items", limit=args.limit)
        
        if args.type:
            cis = [ci for ci in cis if ci.get("type") == args.type]
        if args.status:
            cis = [ci for ci in cis if ci.get("status") == args.status]
        
        result = {"total": len(cis), "configuration_items": cis}
        
        if args.json:
            print_json(result)
        else:
            if not cis:
                print("No configuration items found")
                return
                
            headers = ["ID", "Name", "Type", "Status", "Owner"]
            table_data = []
            for ci in cis:
                table_data.append({
                    "ID": ci.get("sys_id", "N/A")[:8],
                    "Name": ci.get("name", "N/A")[:30],
                    "Type": ci.get("type", "N/A"),
                    "Status": ci.get("status", "N/A"),
                    "Owner": ci.get("owner", "N/A") or "-"
                })
            print_table(table_data, headers)
            
    except Exception as e:
        print(f"✗ Failed to list CIs: {e}")


def cmd_cmdb_show(args: argparse.Namespace) -> None:
    """Show CI details"""
    try:
        cis = json_store.query("configuration_items")
        ci = next((item for item in cis if item.get("sys_id") == args.ci_id or item.get("name") == args.ci_id), None)
        
        if not ci:
            print(f"✗ CI {args.ci_id} not found")
            return
        
        if args.json:
            print_json(ci)
        else:
            print(f"Configuration Item: {ci.get('name', 'N/A')}")
            print(f"ID: {ci.get('sys_id', 'N/A')}")
            print(f"Type: {ci.get('type', 'N/A')}")
            print(f"Class: {ci.get('class', 'N/A')}")
            print(f"Status: {ci.get('status', 'N/A')}")
            print(f"Location: {ci.get('location', 'N/A') or '-'}")
            print(f"Owner: {ci.get('owner', 'N/A') or '-'}")
            
    except Exception as e:
        print(f"✗ Failed to show CI: {e}")


def cmd_cmdb_relate(args: argparse.Namespace) -> None:
    """Create CI relationship"""
    try:
        relationship = {
            "source_ci": args.source_ci,
            "target_ci": args.target_ci,
            "relationship_type": args.type,
            "created": datetime.datetime.now().isoformat()
        }
        
        relationships = json_store.query("ci_relationships")
        relationships.append(relationship)
        json_store.save("ci_relationships", relationships)
        
        result = {"created": True, "relationship": relationship}
        
        if args.json:
            print_json(result)
        else:
            print(f"✓ Created relationship: {args.source_ci} {args.type} {args.target_ci}")
            
    except Exception as e:
        print(f"✗ Failed to create relationship: {e}")


# ========================================
# BUDGET AND FINANCIAL COMMANDS
# ========================================

def cmd_budget_show(args: argparse.Namespace) -> None:
    """Show budget information"""
    try:
        o = ensure_orch()
        dash = o.build_integrated_dashboard()
        budget_info = dash.get("financials", {})
        
        if args.service:
            # Filter budget by service if specified
            budget_info = {k: v for k, v in budget_info.items() if args.service.lower() in str(v).lower()}
        
        if args.json:
            print_json(budget_info)
        else:
            print("Budget Information:")
            print(f"  Total Budget: ${budget_info.get('total_budget', 0):,.2f}")
            print(f"  Total Actual: ${budget_info.get('total_actual', 0):,.2f}")
            print(f"  Variance: ${budget_info.get('variance', 0):,.2f}")
            variance_pct = (budget_info.get('variance', 0) / budget_info.get('total_budget', 1)) * 100
            print(f"  Variance %: {variance_pct:.1f}%")
            
    except Exception as e:
        print(f"✗ Failed to show budget: {e}")


# ========================================
# DATA OPERATION COMMANDS
# ========================================

def cmd_data_backup(args: argparse.Namespace) -> None:
    """Backup data to archive"""
    try:
        import shutil
        import zipfile
        
        backup_path = Path(args.path) if args.path else Path("backups") / f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        data_dir = Path("storage/data")
        
        if not data_dir.exists():
            print("✗ No data directory found")
            return
        
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        if args.compress:
            backup_file = backup_path.with_suffix('.zip')
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in data_dir.rglob('*'):
                    if file_path.is_file():
                        zipf.write(file_path, file_path.relative_to(data_dir))
            print(f"✓ Compressed backup created: {backup_file}")
        else:
            shutil.copytree(data_dir, backup_path, dirs_exist_ok=True)
            print(f"✓ Backup created: {backup_path}")
            
    except Exception as e:
        print(f"✗ Failed to create backup: {e}")


def cmd_data_restore(args: argparse.Namespace) -> None:
    """Restore data from backup"""
    try:
        import shutil
        import zipfile
        
        backup_path = Path(args.path)
        data_dir = Path("storage/data")
        
        if not backup_path.exists():
            print(f"✗ Backup path not found: {backup_path}")
            return
        
        if not args.force and data_dir.exists() and any(data_dir.iterdir()):
            print("✗ Data directory is not empty. Use --force to overwrite.")
            return
        
        # Clear existing data
        if data_dir.exists():
            shutil.rmtree(data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        if backup_path.suffix == '.zip':
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(data_dir)
        else:
            shutil.copytree(backup_path, data_dir, dirs_exist_ok=True)
        
        print(f"✓ Data restored from: {backup_path}")
        
    except Exception as e:
        print(f"✗ Failed to restore data: {e}")


# ========================================
# JOB MANAGEMENT COMMANDS
# ========================================

def cmd_jobs_list(args: argparse.Namespace) -> None:
    """List available jobs"""
    try:
        o = ensure_orch()
        
        # Get available jobs (this would come from the orchestrator)
        jobs = [
            {"name": "periodic_sync", "description": "Sync data between systems", "schedule": "*/30 * * * *"},
            {"name": "metrics_collection", "description": "Collect system metrics", "schedule": "0 */6 * * *"},
            {"name": "cleanup_old_data", "description": "Clean up old log files", "schedule": "0 2 * * 0"},
            {"name": "backup_data", "description": "Backup system data", "schedule": "0 1 * * *"},
            {"name": "security_scan", "description": "Run security scans", "schedule": "0 3 * * 1"}
        ]
        
        result = {"total": len(jobs), "jobs": jobs}
        
        if args.json:
            print_json(result)
        else:
            print("Available Jobs:")
            headers = ["Name", "Description", "Schedule"]
            table_data = []
            for job in jobs:
                table_data.append({
                    "Name": job["name"],
                    "Description": job["description"][:50],
                    "Schedule": job["schedule"]
                })
            print_table(table_data, headers)
            
    except Exception as e:
        print(f"✗ Failed to list jobs: {e}")


# ========================================
# SECURITY COMMANDS
# ========================================

def cmd_security_audit(args: argparse.Namespace) -> None:
    """Security audit"""
    try:
        audit_results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "audit_type": args.type or "general",
            "findings": []
        }
        
        # Simulate audit findings
        if args.type == "access":
            audit_results["findings"] = [
                {"severity": "medium", "finding": "Inactive user accounts detected", "count": 3},
                {"severity": "low", "finding": "Password policy compliance", "count": 1}
            ]
        elif args.type == "config":
            audit_results["findings"] = [
                {"severity": "high", "finding": "Default passwords detected", "count": 1},
                {"severity": "medium", "finding": "Unnecessary services running", "count": 2}
            ]
        elif args.type == "data":
            audit_results["findings"] = [
                {"severity": "low", "finding": "Unencrypted data at rest", "count": 0},
                {"severity": "medium", "finding": "Backup integrity issues", "count": 1}
            ]
        else:
            audit_results["findings"] = [
                {"severity": "medium", "finding": "General security review needed", "count": 5}
            ]
        
        if args.json:
            print_json(audit_results)
        else:
            print(f"Security Audit Report ({args.type or 'general'})")
            print(f"Timestamp: {audit_results['timestamp']}")
            print(f"Findings: {len(audit_results['findings'])}")
            for finding in audit_results["findings"]:
                severity_icon = "🔴" if finding["severity"] == "high" else "🟡" if finding["severity"] == "medium" else "🟢"
                print(f"  {severity_icon} {finding['finding']} (Count: {finding['count']})")
                
    except Exception as e:
        print(f"✗ Failed to run security audit: {e}")


# ========================================
# MATIS TASK AUTOMATION COMMANDS
# ========================================

def cmd_matis_validate(args):
    """Validate Matis installation"""
    try:
        executor = MatisTaskExecutor()
        if executor.validate_matis_installation():
            print("✅ Matis is properly installed and accessible")
            print("📍 Binary location: e:\\Code\\ReasonOps-ITSM\\matis\\target\\release\\matis")
            print("🚀 Ready for task automation execution")
        else:
            print("❌ Matis is not available")
            print("💡 Make sure Matis is built and the binary exists")
    except Exception as e:
        print(f"✗ Failed to validate Matis: {e}")


def cmd_matis_execute(args):
    """Execute a Matis playbook locally"""
    try:
        executor = MatisTaskExecutor()
        
        # Load playbook
        with open(args.playbook, 'r') as f:
            playbook_content = yaml.safe_load(f)
        
        # Load inventory if provided
        inventory_content = None
        if args.inventory:
            with open(args.inventory, 'r') as f:
                inventory_content = yaml.safe_load(f)
        
        # Parse extra vars
        extra_vars = {}
        if args.extra_vars:
            for var in args.extra_vars:
                if '=' in var:
                    key, value = var.split('=', 1)
                    extra_vars[key] = value
        
        result = executor.execute_playbook(
            playbook_content,
            inventory_content,
            extra_vars,
            args.task_id
        )
        
        if result.success:
            print(f"✅ Playbook executed successfully in {result.execution_time:.2f}s")
            if result.output:
                print("Output:")
                print(result.output)
        else:
            print(f"❌ Playbook execution failed: {result.error}")
            if result.output:
                print("Output:")
                print(result.output)
                
    except Exception as e:
        print(f"✗ Failed to execute playbook: {e}")


def cmd_matis_ssh(args):
    """Execute a Matis playbook over SSH"""
    try:
        executor = MatisTaskExecutor()
        
        # Load playbook
        with open(args.playbook, 'r') as f:
            playbook_content = yaml.safe_load(f)
        
        # Load inventory
        with open(args.inventory, 'r') as f:
            inventory_content = yaml.safe_load(f)
        
        result = executor.execute_ssh_playbook(
            playbook_content,
            inventory_content,
            args.user,
            args.key,
            args.threads,
            args.task_id
        )
        
        if result.success:
            print(f"✅ SSH playbook executed successfully in {result.execution_time:.2f}s")
            if result.output:
                print("Output:")
                print(result.output)
        else:
            print(f"❌ SSH playbook execution failed: {result.error}")
            if result.output:
                print("Output:")
                print(result.output)
                
    except Exception as e:
        print(f"✗ Failed to execute SSH playbook: {e}")


def cmd_matis_simulate(args):
    """Simulate Matis playbook execution"""
    try:
        executor = MatisTaskExecutor()
        
        # Load playbook
        with open(args.playbook, 'r') as f:
            playbook_content = yaml.safe_load(f)
        
        # Load inventory if provided
        inventory_content = None
        if args.inventory:
            with open(args.inventory, 'r') as f:
                inventory_content = yaml.safe_load(f)
        
        result = executor.simulate_execution(
            playbook_content,
            inventory_content,
            args.task_id
        )
        
        if result.success:
            print(f"✅ Playbook simulation completed in {result.execution_time:.2f}s")
            if result.output:
                print("Simulation Output:")
                print(result.output)
        else:
            print(f"❌ Playbook simulation failed: {result.error}")
            if result.output:
                print("Output:")
                print(result.output)
                
    except Exception as e:
        print(f"✗ Failed to simulate playbook: {e}")


def cmd_matis_history(args):
    """Show Matis execution history"""
    try:
        executor = MatisTaskExecutor()
        history = executor.get_execution_history(args.limit)
        
        if not history:
            print("No execution history found")
            return
        
        if args.json:
            history_data = []
            for result in history:
                history_data.append({
                    "task_id": result.task_id,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "timestamp": result.timestamp.isoformat(),
                    "error": result.error if result.error else None
                })
            print_json(history_data)
        else:
            print(f"Matis Execution History (Last {len(history)} tasks)")
            print("-" * 80)
            for result in history:
                status = "✅" if result.success else "❌"
                print(f"{status} {result.task_id} - {result.execution_time:.2f}s - {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                if result.error and not result.success:
                    print(f"   Error: {result.error[:100]}{'...' if len(result.error) > 100 else ''}")
            print("-" * 80)
                
    except Exception as e:
        print(f"✗ Failed to retrieve history: {e}")


def cmd_matis_sample(args):
    """Create sample Matis playbook and inventory"""
    try:
        import yaml
        executor = MatisTaskExecutor()
        
        output_dir = Path(args.output) if args.output else Path.cwd()
        output_dir.mkdir(exist_ok=True)
        
        if args.type == "incident-response":
            playbook = executor.create_sample_incident_response_playbook()
            inventory = executor.create_sample_inventory()
            
            playbook_file = output_dir / "incident-response-playbook.yml"
            inventory_file = output_dir / "inventory.yml"
            
            with open(playbook_file, 'w') as f:
                yaml.dump(playbook, f, default_flow_style=False)
            
            with open(inventory_file, 'w') as f:
                yaml.dump(inventory, f, default_flow_style=False)
            
            print("✅ Sample incident response files created:")
            print(f"   📄 Playbook: {playbook_file}")
            print(f"   📋 Inventory: {inventory_file}")
            print("\n🚀 Test with:")
            print(f"   python -m cli matis simulate --playbook {playbook_file} --inventory {inventory_file}")
            
        elif args.type == "inventory":
            inventory = executor.create_sample_inventory()
            inventory_file = output_dir / "inventory.yml"
            
            with open(inventory_file, 'w') as f:
                yaml.dump(inventory, f, default_flow_style=False)
            
            print("✅ Sample inventory created:")
            print(f"   📋 Inventory: {inventory_file}")
                
    except Exception as e:
        print(f"✗ Failed to create sample files: {e}")


def cmd_matis_generate(args):
    """Generate AI-powered automation playbook"""
    try:
        import yaml
        from pathlib import Path

        executor = MatisTaskExecutor()

        # Generate AI-powered playbook
        playbook = executor.generate_automation_playbook(
            incident_description=args.description,
            target_hosts=args.hosts,
            automation_type=args.type
        )

        # Determine output file
        if args.output:
            output_file = Path(args.output)
        else:
            output_file = Path.cwd() / f"ai_generated_{args.type}_playbook.yml"

        # Save playbook
        with open(output_file, 'w') as f:
            yaml.dump(playbook, f, default_flow_style=False)

        print("🤖 AI-Generated automation playbook created:")
        print(f"   📄 Playbook: {output_file}")
        print(f"   🎯 Description: {args.description[:50]}...")
        print(f"   🎯 Type: {args.type}")
        print(f"   🎯 Hosts: {args.hosts}")
        print("\n🚀 Test with:")
        print(f"   python cli.py matis simulate --playbook {output_file}")

    except Exception as e:
        print(f"✗ Failed to generate AI playbook: {e}")


def cmd_matis_incident_playbook(args):
    """Generate incident-specific response playbook"""
    try:
        import yaml
        from pathlib import Path

        executor = MatisTaskExecutor()

        # Generate incident-specific playbook
        playbook = executor.generate_incident_response_playbook(
            incident_title=args.title,
            incident_description=args.description,
            affected_services=args.services
        )

        # Determine output file
        if args.output:
            output_file = Path(args.output)
        else:
            output_file = Path.cwd() / f"incident_response_{args.title.lower().replace(' ', '_')}.yml"

        # Save playbook
        with open(output_file, 'w') as f:
            yaml.dump(playbook, f, default_flow_style=False)

        print("🚨 AI-Generated incident response playbook created:")
        print(f"   📄 Playbook: {output_file}")
        print(f"   🚨 Incident: {args.title}")
        print(f"   📝 Description: {args.description[:50]}...")
        if args.services:
            print(f"   🔧 Affected Services: {', '.join(args.services)}")
        print("\n🚀 Test with:")
        print(f"   python cli.py matis simulate --playbook {output_file}")

    except Exception as e:
        print(f"✗ Failed to generate incident playbook: {e}")
        
        playbook = generator.generate_playbook(
            description=args.description,
            hosts=args.hosts,
            automation_type=args.type
        )
        
        # Save to file if output path is provided
        if args.output:
            with open(args.output, 'w') as f:
                yaml.dump(playbook, f, default_flow_style=False)
            print(f"✅ Playbook generated and saved to: {args.output}")
        else:
            print("✅ Playbook generated:")
            print(yaml.dump(playbook, default_flow_style=False))
            
    except Exception as e:
        print(f"✗ Failed to generate playbook: {e}")


def cmd_matis_incident_playbook(args):
    """Generate incident-specific response playbook"""
    try:
        import yaml
        from pathlib import Path

        executor = MatisTaskExecutor()

        # Generate incident-specific playbook
        playbook = executor.generate_incident_response_playbook(
            incident_title=args.title,
            incident_description=args.description,
            affected_services=args.services
        )

        # Determine output file
        if args.output:
            output_file = Path(args.output)
        else:
            output_file = Path.cwd() / f"incident_response_{args.title.lower().replace(' ', '_')}.yml"

        # Save playbook
        with open(output_file, 'w') as f:
            yaml.dump(playbook, f, default_flow_style=False)

        print("🚨 AI-Generated incident response playbook created:")
        print(f"   📄 Playbook: {output_file}")
        print(f"   🚨 Incident: {args.title}")
        print(f"   📝 Description: {args.description[:50]}...")
        if args.services:
            print(f"   🔧 Affected Services: {', '.join(args.services)}")
        print("\n🚀 Test with:")
        print(f"   python cli.py matis simulate --playbook {output_file}")

    except Exception as e:
        print(f"✗ Failed to generate incident playbook: {e}")


# ========================================
# HELPER FUNCTIONS
# ========================================

def _check_storage_health() -> Dict[str, Any]:
    """Check storage component health"""
    try:
        data_dir = Path("storage/data")
        return {
            "status": "healthy" if data_dir.exists() else "degraded",
            "data_dir_exists": data_dir.exists(),
            "writable": os.access(data_dir, os.W_OK) if data_dir.exists() else False
        }
    except Exception:
        return {"status": "unhealthy", "error": "Failed to check storage"}


def _check_orchestrator_health() -> Dict[str, Any]:
    """Check orchestrator component health"""
    try:
        from integration.orchestrator import ITILOrchestrator
        orch = ITILOrchestrator()
        return {"status": "healthy", "initialized": True}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def _check_agents_health() -> Dict[str, Any]:
    """Check agents component health"""
    try:
        from ai_agents.itil_multi_agent_orchestrator import CollaborativeAgentsOrchestrator
        return {"status": "healthy", "available": True}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}
