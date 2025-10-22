"""
ReasonOps ITSM CLI

Run orchestrated demos, export summaries, and invoke practice workflows.

Usage:
  python -m cli <command> [options]
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from typing import Any, Dict

# Ensure local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.branding import NAME as FRAMEWORK_NAME, VERSION as FRAMEWORK_VERSION, TAGLINE as FRAMEWORK_TAGLINE
from integration.orchestrator import ITILOrchestrator
from ai_agents.itil_multi_agent_orchestrator import CollaborativeAgentsOrchestrator
from storage import json_store


def _to_json_friendly(obj: Any) -> Any:
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
    return obj


def print_json(data: Dict[str, Any]) -> None:
    print(json.dumps(_to_json_friendly(data), indent=2, default=str))


def write_output(data: Dict[str, Any], out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"Wrote: {out_path}")


def cmd_version(args):
    print(f"{FRAMEWORK_NAME} v{FRAMEWORK_VERSION}")
    print(FRAMEWORK_TAGLINE)


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
    # Root-level parser with subparsers for clarity
    parser = argparse.ArgumentParser(prog="ReasonOps ITSM", description=FRAMEWORK_TAGLINE)
    sub = parser.add_subparsers(dest="cmd")

    # version
    sp = sub.add_parser("version", help="Show framework version")
    sp.set_defaults(func=cmd_version)

    # run orchestrator
    sp = sub.add_parser("run:orchestrator", help="Run the integrated orchestrator demo")
    sp.set_defaults(func=cmd_run_orchestrator)

    # run agents
    sp = sub.add_parser("run:agents", help="Run the collaborative agents demo")
    sp.add_argument("--llm-config", dest="llm_config", help="Path to LLM providers config file")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_run_agents)

    # dashboard
    sp = sub.add_parser("dashboard", help="Print integrated dashboard snapshot")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_dashboard)

    # export monthly summary
    sp = sub.add_parser("export:monthly", help="Export current month rollups")
    sp.add_argument("--json", action="store_true")
    sp.add_argument("--out", help="Output file path")
    sp.set_defaults(func=cmd_export_monthly)

    # jobs run
    sp = sub.add_parser("jobs:run", help="Run periodic jobs")
    sp.add_argument("--iterations", type=int, default=1)
    sp.add_argument("--interval", type=int, default=10)
    sp.set_defaults(func=cmd_jobs_run)

    # security simulate
    sp = sub.add_parser("security:simulate", help="Simulate a security event")
    sp.set_defaults(func=cmd_security_simulate)

    # outage record
    sp = sub.add_parser("outage:record", help="Record outage from open incidents")
    sp.add_argument("--minutes", type=float, default=10.0)
    sp.set_defaults(func=cmd_outage_record)

    # slm syncs
    sp = sub.add_parser("slm:sync-availability", help="Sync availability into SLM")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_slm_sync_availability)

    sp = sub.add_parser("slm:sync-outage-availability", help="Sync outage-adjusted availability into SLM")
    sp.add_argument("--days", type=int, default=30)
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_slm_sync_outage_availability)

    sp = sub.add_parser("slm:feed-capacity-kpis", help="Feed capacity KPIs (RT/TP) into SLM")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_slm_feed_capacity_kpis)

    sp = sub.add_parser("slm:metrics", help="Compute SLM metrics (availability, MTTR/MTBF, error budget)")
    sp.add_argument("--days", type=int, default=30)
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_slm_metrics)

    # financial actions
    sp = sub.add_parser("financial:apply-penalties", help="Apply supplier penalties for breach")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_fin_apply_penalties)

    sp = sub.add_parser("financial:apply-chargeback", help="Apply capacity-driven chargebacks")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_fin_apply_chargeback)

    # rollups
    sp = sub.add_parser("rollups:show", help="Show rollups for a collection by month")
    sp.add_argument("--collection", required=True, help="Collection name, e.g., penalties, chargebacks, agent_decisions")
    sp.add_argument("--fields", nargs="+", default=["amount"], help="Fields to sum, e.g., amount penalty count")
    sp.add_argument("--group-by", nargs="+", default=["service"], help="Group-by fields, e.g., service agent_role")
    sp.add_argument("--month", help="YYYY-MM month key (default: current)")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_rollups_show)

    # storage management
    sp = sub.add_parser("storage:clear", help="Delete JSON data files under storage/data")
    sp.add_argument("--yes", action="store_true", help="Confirm deletion without prompt")
    sp.set_defaults(func=cmd_storage_clear)

    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
