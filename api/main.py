from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import sys
import os

from reasonops_sdk import ReasonOpsClient

# Add python-framework to path for agent imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

app = FastAPI(title="ReasonOps ITSM API", version="0.1.0")

# CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = ReasonOpsClient()

# Global instances for agents (lazy-loaded)
llm_router = None
agent_orchestrator = None

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/dashboard")
def get_dashboard():
    d = client.get_dashboard()
    return d.__dict__

@app.get("/api/slm/metrics")
def slm_metrics(period_days: int = Query(30, ge=1, le=180)):
    m = client.compute_slm_metrics(period_days=period_days)
    return m.__dict__

@app.get("/api/slm/metrics/trend")
def slm_metrics_trend(days: int = Query(30, ge=7, le=90)):
    """Return a synthetic trend for availability and burn_rate over the last N days.
    In a real setup, this would aggregate historical SLM records. For demo purposes,
    we generate a stable series with slight variation.
    """
    import datetime as dt
    base = dt.date.today()
    trend = []
    for i in range(days):
        day = base - dt.timedelta(days=(days - 1 - i))
        # simple synthetic variation
        availability = 99.7 + ((i % 5) * 0.05)
        burn_rate = max(0.0, 0.02 - (i % 7) * 0.002)
        trend.append({
            "date": day.isoformat(),
            "availability_pct": round(availability, 3),
            "burn_rate": round(burn_rate, 4),
        })
    return {"days": days, "series": trend}

@app.post("/api/slm/sync-availability")
def slm_sync_availability(lookback_days: int = Query(30, ge=1, le=180)):
    return client.sync_availability(lookback_days=lookback_days)

@app.post("/api/slm/sync-outage-availability")
def slm_sync_outage_availability(lookback_days: int = Query(45, ge=1, le=180)):
    return client.sync_outage_adjusted_availability(lookback_days=lookback_days)

@app.post("/api/capacity/feed-kpis")
def capacity_feed_kpis(lookback_days: int = Query(30, ge=1, le=180)):
    return client.feed_capacity_kpis(lookback_days=lookback_days)

@app.post("/api/financial/apply-penalties")
def financial_apply_penalties():
    return client.apply_supplier_penalties()

@app.post("/api/financial/apply-chargeback")
def financial_apply_chargeback():
    return client.apply_capacity_chargeback()

@app.get("/api/summary/monthly")
def export_monthly(month: Optional[str] = Query(None, description="YYYY-MM")):
    s = client.export_monthly_summary(month=month)
    return s.__dict__

@app.post("/api/jobs/run")
def jobs_run():
    return client.run_periodic_jobs()

@app.post("/api/storage/clear")
def storage_clear():
    client.clear_storage()
    return {"cleared": True}


# ========================================
# AI Agent Endpoints
# ========================================

class AgentRunRequest(BaseModel):
    event_type: str  # "incident", "capacity_alert", "outage", etc.
    event_data: Dict[str, Any]
    llm_provider: Optional[str] = "ollama"


class LLMConfigRequest(BaseModel):
    provider: str  # "ollama", "openai", "anthropic", etc.
    model: Optional[str] = None
    api_key: Optional[str] = None
    temperature: Optional[float] = 0.7


def _init_agent_orchestrator():
    """Lazy initialize agent orchestrator with LLM router"""
    global llm_router, agent_orchestrator
    
    if agent_orchestrator is None:
        try:
            # Import from correct path
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python-framework'))
            
            from ai_agents.multi_llm_provider import (
                LLMConfig, LLMProvider, ModelType, get_provider_instance
            )
            from ai_agents.llm_router import EnhancedLLMRouter
            from ai_agents.itil_multi_agent_orchestrator import CollaborativeAgentsOrchestrator
            
            # Create default Ollama config (fallback to mock if unavailable)
            configs = []
            
            # Try Ollama first
            try:
                ollama_config = LLMConfig(
                    provider=LLMProvider.OLLAMA,
                    model=ModelType.LLAMA2_7B,
                    base_url="http://localhost:11434"
                )
                configs.append(get_provider_instance(ollama_config))
            except Exception as e:
                print(f"Ollama not available: {e}")
            
            # Add mock as fallback
            mock_config = LLMConfig(provider=LLMProvider.MOCK, model=ModelType.MOCK_MODEL)
            configs.append(get_provider_instance(mock_config))
            
            # Create router with fallback chain
            llm_router = EnhancedLLMRouter(configs)
            
            # Create orchestrator
            agent_orchestrator = CollaborativeAgentsOrchestrator(
                base_provider_config=configs[0].config if configs else mock_config
            )
            
            print("✓ Agent orchestrator initialized with LLM router")
            
        except Exception as e:
            print(f"Failed to initialize agents: {e}")
            raise HTTPException(status_code=500, detail=f"Agent initialization failed: {e}")
    
    return agent_orchestrator


@app.post("/api/agents/run")
async def run_agents(request: AgentRunRequest, background_tasks: BackgroundTasks):
    """
    Execute agent orchestration for an event
    
    Example:
    {
        "event_type": "incident",
        "event_data": {
            "incident_id": "INC001",
            "severity": "high",
            "description": "Service outage"
        }
    }
    """
    orchestrator = _init_agent_orchestrator()
    
    try:
        # Run agent decision-making
        result = await orchestrator.handle_event(
            event_type=request.event_type,
            event_data=request.event_data
        )
        
        return {
            "status": "success",
            "event_type": request.event_type,
            "decisions": result.get("decisions", []),
            "actions_taken": result.get("actions", []),
            "timestamp": result.get("timestamp")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/decisions")
def get_agent_decisions(
    limit: int = Query(50, ge=1, le=500),
    event_type: Optional[str] = None,
    agent_name: Optional[str] = None
):
    """Get agent decision history with optional filters"""
    orchestrator = _init_agent_orchestrator()
    
    try:
        # Get decisions from orchestrator's storage
        decisions = orchestrator.get_decision_history(
            limit=limit,
            event_type=event_type,
            agent_name=agent_name
        )
        
        return {
            "total": len(decisions),
            "decisions": decisions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/configure-llm")
def configure_llm(config: LLMConfigRequest):
    """Configure active LLM provider"""
    global llm_router, agent_orchestrator
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python-framework'))
        
        from ai_agents.multi_llm_provider import (
            LLMConfig, LLMProvider, ModelType, get_provider_instance
        )
        from ai_agents.llm_router import EnhancedLLMRouter
        
        # Map string to enum
        provider_map = {
            "ollama": LLMProvider.OLLAMA,
            "openai": LLMProvider.OPENAI,
            "anthropic": LLMProvider.ANTHROPIC,
            "google": LLMProvider.GOOGLE,
            "azure": LLMProvider.AZURE_OPENAI,
            "huggingface": LLMProvider.HUGGINGFACE,
            "mock": LLMProvider.MOCK
        }
        
        provider_enum = provider_map.get(config.provider.lower())
        if not provider_enum:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown provider: {config.provider}. Valid: {list(provider_map.keys())}"
            )
        
        # Create new provider config
        llm_config = LLMConfig(
            provider=provider_enum,
            model=ModelType.LLAMA2_7B if not config.model else config.model,
            api_key=config.api_key,
            temperature=config.temperature,
            base_url="http://localhost:11434" if provider_enum == LLMProvider.OLLAMA else None
        )
        
        # Reinitialize router
        provider_instance = get_provider_instance(llm_config)
        llm_router = EnhancedLLMRouter([provider_instance])
        
        # Reset orchestrator to pick up new config
        agent_orchestrator = None
        
        return {
            "status": "success",
            "message": f"LLM provider configured: {config.provider}",
            "config": {
                "provider": config.provider,
                "model": config.model or "default"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/health")
async def check_agent_health():
    """Check health of all configured LLM providers"""
    if llm_router is None:
        _init_agent_orchestrator()
    
    if llm_router:
        # Trigger a health check
        await llm_router._check_all_providers()
        health_summary = llm_router.get_health_summary()
        
        return {
            "status": "ok",
            "providers": health_summary,
            "router_active": True
        }
    else:
        return {
            "status": "not_initialized",
            "providers": {},
            "router_active": False
        }


@app.get("/api/agents/providers")
def list_llm_providers():
    """List all available LLM providers and models"""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python-framework'))
        
        from ai_agents.multi_llm_provider import LLMProvider, ModelType
        
        return {
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Entrypoint for local run: uvicorn api.main:app --reload

