import unittest
import json
from generator import ScenarioGenerator, SpoofingInjector
from utils import to_canonical_json

class TestSpoofingInjector(unittest.TestCase):
    def setUp(self):
        self.gen = ScenarioGenerator(seed=42)
        self.clean_scenario = self.gen.generate_clean_scenario("SUI/USDC", 20)

    def test_injection_determinism(self):
        """Verify injection is deterministic with the same seed."""
        seed = 888
        inj1 = SpoofingInjector(seed)
        res1 = inj1.inject_spoofing(self.clean_scenario)
        
        inj2 = SpoofingInjector(seed)
        res2 = inj2.inject_spoofing(self.clean_scenario)
        
        self.assertEqual(to_canonical_json(res1), to_canonical_json(res2))

    def test_manipulated_structure(self):
        """Verify ground truth and event count after injection."""
        seed = 777
        injector = SpoofingInjector(seed)
        result = injector.inject_spoofing(self.clean_scenario)
        
        self.assertEqual(result["ground_truth"]["label"], "manipulated")
        self.assertEqual(result["ground_truth"]["manipulation_type"], "spoofing")
        # Should have 2 more events than clean (place + cancel)
        self.assertEqual(len(result["events"]), len(self.clean_scenario["events"]) + 2)
        
        # Check that implicated IDs are actually in the events list
        implicated = result["ground_truth"]["implicated_event_ids"]
        self.assertEqual(len(implicated), 2)
        event_ids = [e["event_id"] for e in result["events"]]
        for eid in implicated:
            self.assertIn(eid, event_ids)

    def test_timestamp_sorting_maintained(self):
        """Verify that events remain sorted after injection."""
        injector = SpoofingInjector(seed=123)
        result = injector.inject_spoofing(self.clean_scenario)
        
        timestamps = [e["ts"] for e in result["events"]]
        self.assertEqual(timestamps, sorted(timestamps))

if __name__ == "__main__":
    unittest.main()