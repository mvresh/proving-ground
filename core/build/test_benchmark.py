import unittest
import json
import io
from unittest.mock import patch, MagicMock
from proving_ground import main

class TestBenchmarkCommand(unittest.TestCase):
    def setUp(self):
        # Reset arguments for each test
        self.base_args = ["proving_ground.py", "benchmark", "--count", "2", "--seed", "123"]

    @patch('llm_provider.get_provider')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_benchmark_success_stub(self, mock_stdout, mock_get_provider):
        # Setup mock provider
        mock_p = MagicMock()
        mock_p.complete.return_value = {
            "text": json.dumps({
                "flagged": False,
                "predicted_type": None,
                "flagged_event_ids": [],
                "confidence": 0.5,
                "rationale": "Test rationale"
            }),
            "input_tokens": 10,
            "output_tokens": 5
        }
        mock_p.get_cost.return_value = 0
        mock_get_provider.return_value = mock_p

        with patch('sys.argv', self.base_args):
            try:
                main()
            except SystemExit as e:
                self.assertEqual(e.code, 0)

        output = json.loads(mock_stdout.getvalue())
        self.assertIn("scenario_set_hash", output)
        self.assertEqual(len(output["detectors"]), 2)
        self.assertEqual(output["detectors"][0]["detector_id"], "heuristic_v1")
        self.assertEqual(output["detectors"][1]["detector_id"], "llm_v1")
        self.assertEqual(output["cost_nano_usd"], 0)

    @patch('llm_provider.get_provider')
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_benchmark_provider_failure(self, mock_stderr, mock_get_provider):
        # Setup mock provider to raise error
        mock_p = MagicMock()
        mock_p.complete.side_effect = Exception("Connection Refused")
        mock_get_provider.return_value = mock_p

        with patch('sys.argv', self.base_args):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertNotEqual(cm.exception.code, 0)

        err_msg = mock_stderr.getvalue()
        self.assertIn("[BENCHMARK]", err_msg)
        self.assertIn("Connection Refused", err_msg)

    @patch('llm_provider.get_provider')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_benchmark_cost_aggregation(self, mock_stdout, mock_get_provider):
        # Setup mock provider with cost
        mock_p = MagicMock()
        mock_p.complete.return_value = {
            "text": json.dumps({"flagged": False, "predicted_type": None, "flagged_event_ids": [], "confidence": 0, "rationale": ""}),
            "input_tokens": 1, "output_tokens": 1
        }
        # Return 500 nano USD per call. With count=2, total should be 1000.
        mock_p.get_cost.return_value = 500
        mock_get_provider.return_value = mock_p

        with patch('sys.argv', self.base_args):
            try:
                main()
            except SystemExit:
                pass

        output = json.loads(mock_stdout.getvalue())
        self.assertEqual(output["cost_nano_usd"], 1000)

if __name__ == "__main__":
    unittest.main()