import unittest
from scorer import ScoringEngine

class TestScoringEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ScoringEngine()

    def test_perfect_detection(self):
        scenario_set = [
            {"scenario_id": "scn_1", "ground_truth": {"label": "manipulated", "manipulation_type": "spoofing", "explanation": "x"}},
            {"scenario_id": "scn_2", "ground_truth": {"label": "clean", "manipulation_type": None, "explanation": "y"}}
        ]
        detections = [
            {"scenario_id": "scn_1", "flagged": True},
            {"scenario_id": "scn_2", "flagged": False}
        ]
        result = self.engine.calculate_run_result(scenario_set, detections)
        
        self.assertEqual(result["metrics"]["catch_rate"], 1.0)
        self.assertEqual(result["metrics"]["false_positive_rate"], 0.0)
        self.assertEqual(result["metrics"]["precision"], 1.0)
        self.assertEqual(len(result["misses"]), 0)

    def test_miss_and_false_positive(self):
        scenario_set = [
            {"scenario_id": "scn_1", "ground_truth": {"label": "manipulated", "manipulation_type": "spoofing", "explanation": "missed spoof"}},
            {"scenario_id": "scn_2", "ground_truth": {"label": "clean", "manipulation_type": None, "explanation": "clean scenario"}}
        ]
        detections = [
            {"scenario_id": "scn_1", "flagged": False}, # FN
            {"scenario_id": "scn_2", "flagged": True}   # FP
        ]
        result = self.engine.calculate_run_result(scenario_set, detections)
        
        self.assertEqual(result["metrics"]["catch_rate"], 0.0)
        self.assertEqual(result["metrics"]["false_positive_rate"], 1.0)
        self.assertEqual(result["metrics"]["precision"], 0.0)
        self.assertEqual(len(result["misses"]), 1)
        self.assertEqual(result["misses"][0]["scenario_id"], "scn_1")

    def test_mismatched_ids_raises_error(self):
        scenario_set = [{"scenario_id": "scn_1", "ground_truth": {"label": "clean"}}]
        detections = [{"scenario_id": "scn_wrong", "flagged": False}]
        with self.assertRaisesRegex(ValueError, "ID mismatch"):
            self.engine.calculate_run_result(scenario_set, detections)

if __name__ == "__main__":
    unittest.main()