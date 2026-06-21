import unittest
import json
from detector import LLMDetector
from llm_provider import StubProvider

class TestLLMDetector(unittest.TestCase):
    def test_stub_llm_detector_determinism(self):
        provider = StubProvider()
        detector = LLMDetector(provider, model_id="stub-detector-v1")
        
        # Scenario where one order is 5x median
        scenario = {
            "scenario_id": "scn_1",
            "events": [
                {"event_id": "e1", "ts": 10, "type": "place", "size": 1.0, "owner_id": "t1"},
                {"event_id": "e2", "ts": 20, "type": "place", "size": 1.0, "owner_id": "t1"},
                {"event_id": "e3", "ts": 30, "type": "place", "size": 10.0, "owner_id": "t2"} # 10x median (1)
            ]
        }
        
        res1 = detector.detect(scenario)
        res2 = detector.detect(scenario)
        
        self.assertEqual(res1, res2)
        self.assertTrue(res1["flagged"])
        self.assertIn("e3", res1["flagged_event_ids"])
        self.assertEqual(detector.total_cost_nano_usd, 0)

    def test_stub_llm_detector_clean(self):
        provider = StubProvider()
        detector = LLMDetector(provider, model_id="stub-detector-v1")
        
        scenario = {
            "scenario_id": "scn_2",
            "events": [
                {"event_id": "e1", "ts": 10, "type": "place", "size": 1.0, "owner_id": "t1"},
                {"event_id": "e2", "ts": 20, "type": "place", "size": 1.1, "owner_id": "t1"}
            ]
        }
        
        res = detector.detect(scenario)
        self.assertFalse(res["flagged"])

    def test_detector_failure_raises(self):
        class FailingProvider:
            def complete(self, **kwargs):
                raise RuntimeError("Service down")
            def get_cost(self, *args): return 0

        detector = LLMDetector(FailingProvider())
        with self.assertRaises(RuntimeError) as cm:
            detector.detect({"scenario_id": "fail_me"})
        self.assertIn("LLM detection failed", str(cm.exception))

if __name__ == "__main__":
    unittest.main()