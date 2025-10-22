from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from reasonops_sdk import ReasonOpsClient

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

# Entrypoint for local run: uvicorn api.main:app --reload
