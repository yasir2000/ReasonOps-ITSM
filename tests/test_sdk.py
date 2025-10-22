import pytest


def test_sdk_client_basic():
    # Import here to ensure package path resolution matches test runner
    from reasonops_sdk import ReasonOpsClient

    client = ReasonOpsClient()

    # Basic dashboard shape
    dashboard = client.get_dashboard()
    assert hasattr(dashboard, "services")
    assert hasattr(dashboard, "offerings")
    assert isinstance(dashboard.service_level, dict)

    # SLM metrics shape
    metrics = client.compute_slm_metrics(period_days=1)
    assert hasattr(metrics, "availability_pct")
    assert hasattr(metrics, "error_budget")
    assert isinstance(metrics.error_budget, dict)
