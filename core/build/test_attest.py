import unittest
import json
import sys
from io import StringIO
from unittest.mock import patch, MagicMock
import commands

class TestAttestCommand(unittest.TestCase):
    def setUp(self):
        self.valid_run_result = {
            "run_id": "run_123",
            "detector_id": "heuristic_v1",
            "timestamp": "2026-06-20T12:00:00Z",
            "scenario_set_hash": "a" * 64,
            "metrics": {"catch_rate": 1.0, "false_positive_rate": 0.0, "precision": 1.0, "by_type": {}},
            "misses": []
        }

    @patch("blob_store.StubBlobStore.store")
    @patch("sys.stdin", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_attest_success(self, mock_stdout, mock_stdin, mock_store):
        mock_stdin.write(json.dumps(self.valid_run_result))
        mock_stdin.seek(0)
        mock_store.return_value = "stub_mock_id"

        args = MagicMock()
        args.store = "stub"
        
        commands.cmd_attest(args)
        
        output = json.loads(mock_stdout.getvalue())
        self.assertEqual(output["run_id"], "run_123")
        self.assertEqual(output["blob_id"], "stub_mock_id")
        self.assertEqual(output["store"], "stub")

    @patch("blob_store.get_blob_store")
    @patch("sys.stdin", new_callable=StringIO)
    def test_attest_failure_exits(self, mock_stdin, mock_get_store):
        mock_stdin.write(json.dumps(self.valid_run_result))
        mock_stdin.seek(0)
        
        # Make the store raise an error
        mock_store_instance = MagicMock()
        mock_store_instance.store.side_effect = Exception("Storage full")
        mock_get_store.return_value = mock_store_instance

        args = MagicMock()
        args.store = "stub"

        with self.assertRaises(SystemExit) as cm:
            commands.cmd_attest(args)
        self.assertNotEqual(cm.exception.code, 0)

if __name__ == "__main__":
    unittest.main()