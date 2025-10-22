import os
import unittest
from decimal import Decimal
from integration.orchestrator import ITILOrchestrator
from storage import json_store


class TestOrchestratorFlows(unittest.TestCase):
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

    def test_penalty_posting_persists_record(self):
        orch = ITILOrchestrator()
        # Ensure availability and KPI targets exist
        orch.sync_availability_into_slm()
        orch.feed_capacity_metrics_into_slm()
        # Simulate breach and apply penalties
        orch.simulate_sla_breach()
        total = orch.apply_supplier_penalties_for_breaches()
        self.assertTrue(total > Decimal('0.00'))
        records = json_store.read_all('penalties')
        self.assertTrue(len(records) >= 1)
        last = records[-1]
        self.assertIn('service', last)
        self.assertIn('penalty', last)

    def test_availability_records_into_slm(self):
        orch = ITILOrchestrator()
        av = orch.sync_availability_into_slm()
        self.assertIsNotNone(av)
        # Find availability measurements for Customer Portal
        measures = [m for m in orch.slm.measurements if orch.slm.get_agreement(m.agreement_id).service_name.startswith('Customer Portal')]
        self.assertTrue(any(abs(m.actual_value - av) < 0.001 for m in measures))


if __name__ == '__main__':
    unittest.main()
