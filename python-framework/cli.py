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

    # AI Agent commands
    sp = sub.add_parser("agents:run", help="Execute AI agent orchestration for an event")
    sp.add_argument("--event-type", required=True, help="Event type (incident, capacity_alert, outage)")
    sp.add_argument("--event-data", required=True, help="Event data as JSON string")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_agents_run)

    sp = sub.add_parser("agents:list-decisions", help="List agent decision history")
    sp.add_argument("--limit", type=int, default=50, help="Max number of decisions to retrieve")
    sp.add_argument("--event-type", help="Filter by event type")
    sp.add_argument("--agent-name", help="Filter by agent name")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_agents_list_decisions)

    sp = sub.add_parser("agents:configure-llm", help="Configure LLM provider for agents")
    sp.add_argument("--provider", required=True, help="LLM provider (ollama, openai, anthropic, etc.)")
    sp.add_argument("--model", help="Model name (e.g., llama2-7b, gpt-4)")
    sp.add_argument("--api-key", help="API key for provider")
    sp.add_argument("--temperature", type=float, default=0.7, help="Temperature (0.0-1.0)")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_agents_configure_llm)

    sp = sub.add_parser("agents:health", help="Check health of LLM providers")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_agents_health)

    sp = sub.add_parser("agents:list-providers", help="List available LLM providers and models")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_agents_list_providers)

    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    args.func(args)


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
    from ai_agents.multi_llm_provider import LLMConfig, LLMProvider, ModelType, get_provider_instance
    from ai_agents.llm_router import EnhancedLLMRouter
    
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
    
    llm_config = LLMConfig(
        provider=provider_enum,
        model=args.model or ModelType.LLAMA2_7B,
        api_key=args.api_key,
        temperature=args.temperature,
        base_url="http://localhost:11434" if provider_enum == LLMProvider.OLLAMA else None
    )
    
    result = {
        "status": "success",
        "provider": args.provider,
        "model": args.model or "default",
        "message": f"LLM provider configured: {args.provider}"
    }
    
    if args.json:
        print_json(result)
    else:
        print(f"✓ {result['message']}")
        print(f"  Model: {result['model']}")


def cmd_agents_health(args: argparse.Namespace) -> None:
    """Check LLM provider health"""
    import asyncio
    from ai_agents.multi_llm_provider import LLMConfig, LLMProvider, ModelType, get_provider_instance
    from ai_agents.llm_router import EnhancedLLMRouter
    
    # Create a router with available providers
    configs = []
    
    # Try Ollama
    try:
        ollama_config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model=ModelType.LLAMA2_7B,
            base_url="http://localhost:11434"
        )
        configs.append(get_provider_instance(ollama_config))
    except Exception:
        pass
    
    # Add mock
    mock_config = LLMConfig(provider=LLMProvider.MOCK, model=ModelType.MOCK_MODEL)
    configs.append(get_provider_instance(mock_config))
    
    router = EnhancedLLMRouter(configs)
    
    async def check():
        await router._check_all_providers()
        return router.get_health_summary()
    
    health_summary = asyncio.run(check())
    
    result = {
        "status": "ok",
        "providers": health_summary,
        "router_active": True
    }
    
    if args.json:
        print_json(result)
    else:
        print("LLM Provider Health:")
        for provider, health in health_summary.items():
            status_icon = "✓" if health["status"] == "healthy" else "⚠" if health["status"] == "degraded" else "✗"
            print(f"  {status_icon} {provider}: {health['status']}")
            if health.get("latency_ms"):
                print(f"    Latency: {health['latency_ms']:.0f}ms")
            if health.get("message"):
                print(f"    Message: {health['message']}")


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


if __name__ == "__main__":
    main()
