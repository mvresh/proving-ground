import unittest
from detector import HeuristicDetector

class TestHeuristicDetector(unittest.TestCase):
    def setUp(self):
        self.detector = HeuristicDetector(size_threshold=50.0, time_threshold_ms=500)

    def test_detect_clean_scenario(self):
        scenario = {
            "scenario_id": "scn_clean",
            "events": [
                {"event_id": "e1", "ts": 100, "type": "place", "order_id": "o1", "side": "bid", "price": 10.0, "size": 1.0, "owner_id": "t1"}
            ]
        }
        result = self.detector.detect(scenario)
        self.assertFalse(result["flagged"])
        self.assertEqual(len(result["flagged_event_ids"]), 0)

    def test_detect_spoofing(self):
        scenario = {
            "scenario_id": "scn_spoof",
            "events": [
                {"event_id": "e1", "ts": 100, "type": "place", "order_id": "o1", "side": "bid", "price": 10.0, "size": 100.0, "owner_id": "t1"},
                {"event_id": "e2", "ts": 200, "type": "cancel", "order_id": "o1", "side": "bid", "price": 10.0, "size": 100.0, "owner_id": "t1"}
            ]
        }
        result = self.detector.detect(scenario)
        self.assertTrue(result["flagged"])
        self.assertEqual(result["predicted_type"], "spoofing")
        self.assertIn("e1", result["flagged_event_ids"])
        self.assertIn("e2", result["flagged_event_ids"])

    def test_detect_no_flag_on_trade(self):
        # Even if size is large, if it's traded, it's not a spoof by our heuristic
        scenario = {
            "scenario_id": "scn_trade",
            "events": [
                {"event_id": "e1", "ts": 100, "type": "place", "order_id": "o1", "side": "bid", "price": 10.0, "size": 100.0, "owner_id": "t1"},
                {"event_id": "e2", "ts": 150, "type": "trade", "order_id": "o1", "side": "bid", "price": 10.0, "size": 100.0, "owner_id": "t2"},
                {"event_id": "e3", "ts": 200, "type": "cancel", "order_id": "o1", "side": "bid", "price": 10.0, "size": 100.0, "owner_id": "t1"}
            ]
        }
        result = self.detector.detect(scenario)
        self.assertFalse(result["flagged"])

if __name__ == "__main__":
    unittest.main()