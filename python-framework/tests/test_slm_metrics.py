import os
import unittest
from datetime import datetime, timedelta
from integration.orchestrator import ITILOrchestrator


class TestSLMMetrics(unittest.TestCase):
    def setUp(self):
        # Clean persistence files for deterministic tests
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'storage', 'data')
        if os.path.isdir(data_dir):
            for fn in os.listdir(data_dir):
                if fn.endswith('.json'):
                    try:
                        os.remove(os.path.join(data_dir, fn))
                    except Exception:
                        pass

    def test_error_budget_burn_rate_and_mttr_mtbf(self):
        orch = ITILOrchestrator()
        # Ensure an agreement exists
        orch.sync_availability_into_slm()
        # Record two outages with known spacing within 1 day
        service_name = "Customer Portal"
        svc_id = orch.availability_map.get(service_name, "SVC-001")
        now = datetime.now()
        from practices.availability_management import ServiceOutage, OutageType
        o1 = ServiceOutage(
            service_id=svc_id, service_name=service_name, outage_type=OutageType.UNPLANNED,
            start_time=now - timedelta(hours=5), end_time=now - timedelta(hours=4, minutes=30),
            duration_minutes=30, affected_users=10, affected_business_functions=["Login"],
            root_cause="Test1", resolution_summary="Restored"
        )
        orch.availability.record_outage(o1)
        o2 = ServiceOutage(
            service_id=svc_id, service_name=service_name, outage_type=OutageType.UNPLANNED,
            start_time=now - timedelta(hours=2), end_time=now - timedelta(hours=1, minutes=30),
            duration_minutes=30, affected_users=20, affected_business_functions=["Checkout"],
            root_cause="Test2", resolution_summary="Restored"
        )
        orch.availability.record_outage(o2)

        metrics = orch.compute_slm_metrics(period_days=1)
        # Availability should be less than 100
        self.assertLess(metrics["availability_pct"], 100.0)
        # MTTR approx 30 minutes
        self.assertAlmostEqual(metrics["mttr_minutes"], 30.0, places=2)
        # MTBF ~ gap between outages: from first end (4:30h ago) to second start (2h ago) = 2.5h
        self.assertAlmostEqual(metrics["mtbf_hours"], 2.5, places=1)
        # Error budget exists and burn_rate is numeric
        eb = metrics["error_budget"]
        self.assertIn("burn_rate", eb)
        self.assertIsInstance(eb["burn_rate"], float)


if __name__ == '__main__':
    unittest.main()
