import unittest
import json
from generator import ScenarioGenerator
from utils import to_canonical_json

class TestScenarioGenerator(unittest.TestCase):
    def test_determinism(self):
        """Verify that the same seed produces the identical scenario."""
        seed = 12345
        gen1 = ScenarioGenerator(seed)
        scn1 = gen1.generate_clean_scenario("SUI/USDC", 10)
        
        gen2 = ScenarioGenerator(seed)
        scn2 = gen2.generate_clean_scenario("SUI/USDC", 10)
        
        self.assertEqual(to_canonical_json(scn1), to_canonical_json(scn2))

    def test_scenario_structure(self):
        """Verify that the generated scenario matches the schema requirements."""
        gen = ScenarioGenerator(seed=99)
        num_events = 20
        scn = gen.generate_clean_scenario("BTC/USDC", num_events)
        
        self.assertEqual(len(scn["events"]), num_events)
        self.assertEqual(scn["ground_truth"]["label"], "clean")
        self.assertIsNone(scn["ground_truth"]["manipulation_type"])
        self.assertEqual(len(scn["ground_truth"]["implicated_event_ids"]), 0)
        
        # Check timestamp ordering
        timestamps = [e["ts"] for e in scn["events"]]
        self.assertEqual(timestamps, sorted(timestamps))

    def test_canonical_json(self):
        """Verify keys are sorted and no extra whitespace exists."""
        data = {"b": 1, "a": 2, "c": {"z": 0, "y": 1}}
        expected = '{"a":2,"b":1,"c":{"y":1,"z":0}}'
        self.assertEqual(to_canonical_json(data), expected)

if __name__ == "__main__":
    unittest.main()