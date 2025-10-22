import os
import unittest
from datetime import datetime
from integration.orchestrator import ITILOrchestrator
from storage import json_store


class TestMonthlyRollupsAndDashboard(unittest.TestCase):
    def setUp(self):
        # Clean persistence for deterministic tests
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'storage', 'data')
        if os.path.isdir(data_dir):
            for fn in os.listdir(data_dir):
                if fn.endswith('.json'):
                    try:
                        os.remove(os.path.join(data_dir, fn))
                    except Exception:
                        pass

    def test_monthly_rollups_penalties_and_chargebacks(self):
        orch = ITILOrchestrator()
        # Generate data: breach -> penalties, capacity -> chargebacks
        orch.simulate_sla_breach()
        penalties = orch.apply_supplier_penalties_for_breaches()
        chargebacks = orch.apply_capacity_chargeback()
        self.assertGreaterEqual(float(penalties), 0.0)
        self.assertGreater(float(chargebacks), 0.0)

        mk = json_store.month_key(datetime.now())
        pen_roll = json_store.rollup_monthly("penalties", "timestamp", ["penalty"], group_by=["service"]) 
        chg_roll = json_store.rollup_monthly("chargebacks", "timestamp", ["amount"], group_by=["service"]) 
        self.assertIn(mk, pen_roll)
        self.assertIn(mk, chg_roll)
        total_pen = sum(v.get("penalty", 0.0) for v in pen_roll.get(mk, {}).values()) if isinstance(pen_roll.get(mk), dict) else 0.0
        total_chg = sum(v.get("amount", 0.0) for v in chg_roll.get(mk, {}).values()) if isinstance(chg_roll.get(mk), dict) else 0.0
        self.assertGreaterEqual(total_pen, 0.0)
        self.assertGreater(total_chg, 0.0)

    def test_dashboard_structure_and_values(self):
        orch = ITILOrchestrator()
        dash = orch.build_integrated_dashboard()
        # Basic keys
        for key in ("services", "offerings", "service_level", "security", "suppliers", "financials", "history"):
            self.assertIn(key, dash)
        # Types
        self.assertIsInstance(dash["services"], int)
        self.assertIsInstance(dash["offerings"], int)
        self.assertIn("monthly_penalties", dash["history"])
        self.assertIn("monthly_chargebacks", dash["history"])

    def test_outage_adjusted_availability_regression(self):
        orch = ITILOrchestrator()
        # Ensure an open incident exists so an outage can be recorded
        orch.simulate_security_event()
        # Record a fixed 60-minute outage and sync availability for a 1-day window
        outage_id = orch.record_outage_from_incidents(minutes=60.0)
        self.assertIsNotNone(outage_id)
        availability_pct = orch.sync_outage_adjusted_availability_into_slm(period_days=1)
        self.assertIsNotNone(availability_pct)
        # Expected availability: (1440 - 60) / 1440 * 100
        expected = (1440.0 - 60.0) / 1440.0 * 100.0
        self.assertAlmostEqual(availability_pct, expected, places=2)


if __name__ == '__main__':
    unittest.main()
