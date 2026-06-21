import unittest
import json
from generator import ScenarioSetGenerator
from utils import to_canonical_json

class TestScenarioSetGenerator(unittest.TestCase):
    def test_set_determinism(self):
        """Verify that the same seed produces the identical scenario set."""
        seed = 555
        gen1 = ScenarioSetGenerator(seed)
        set1 = gen1.generate_set(count=5, fraction=0.4, market="SUI/USDC", events_per_scenario=10)
        
        gen2 = ScenarioSetGenerator(seed)
        set2 = gen2.generate_set(count=5, fraction=0.4, market="SUI/USDC", events_per_scenario=10)
        
        self.assertEqual(to_canonical_json(set1), to_canonical_json(set2))

    def test_manipulation_fraction(self):
        """Verify that the requested fraction of scenarios are manipulated."""
        count = 20
        fraction = 0.25 # Expected 5 manipulated
        gen = ScenarioSetGenerator(seed=123)
        scenario_set = gen.generate_set(count=count, fraction=fraction, market="SUI/USDC", events_per_scenario=10)
        
        manipulated = [s for s in scenario_set if s["ground_truth"]["label"] == "manipulated"]
        self.assertEqual(len(manipulated), 5)
        
        clean = [s for s in scenario_set if s["ground_truth"]["label"] == "clean"]
        self.assertEqual(len(clean), 15)

    def test_unique_scenario_ids(self):
        """Verify that all scenarios in a set have unique IDs."""
        gen = ScenarioSetGenerator(seed=999)
        scenario_set = gen.generate_set(count=10, fraction=0.5, market="SUI/USDC", events_per_scenario=5)
        
        ids = [s["scenario_id"] for s in scenario_set]
        self.assertEqual(len(ids), len(set(ids)), "Scenario IDs must be unique")

    def test_invalid_fraction(self):
        """Verify that invalid fractions raise an error."""
        gen = ScenarioSetGenerator(seed=1)
        with self.assertRaises(ValueError):
            gen.generate_set(count=1, fraction=1.1, market="SUI/USDC", events_per_scenario=1)
        with self.assertRaises(ValueError):
            gen.generate_set(count=1, fraction=-0.1, market="SUI/USDC", events_per_scenario=1)

if __name__ == "__main__":
    unittest.main()