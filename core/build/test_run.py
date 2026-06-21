import unittest
import json
import subprocess
import sys
import os

class TestRunCommand(unittest.TestCase):
    def test_run_command_output_structure(self):
        """Verify that the run command returns a valid RunResult structure."""
        cmd = [
            sys.executable, "proving_ground.py", "run",
            "--seed", "123",
            "--count", "2",
            "--manipulated-fraction", "0.5"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Run command failed: {result.stderr}")
        
        data = json.loads(result.stdout)
        
        # Check required fields from schema
        required_fields = ["run_id", "detector_id", "timestamp", "scenario_set_hash", "metrics", "misses"]
        for field in required_fields:
            self.assertIn(field, data)
            
        self.assertTrue(data["run_id"].startswith("run_"))
        self.assertEqual(data["detector_id"], "heuristic_v1")
        self.assertEqual(len(data["scenario_set_hash"]), 64) # SHA-256
        
        # Check metrics
        metrics = data["metrics"]
        self.assertIn("catch_rate", metrics)
        self.assertIn("false_positive_rate", metrics)
        self.assertIn("by_type", metrics)
        self.assertIn("spoofing", metrics["by_type"])

    def test_run_determinism(self):
        """Verify that same seed produces identical run results (except for ID and timestamp)."""
        cmd = [
            sys.executable, "proving_ground.py", "run",
            "--seed", "999",
            "--count", "5"
        ]
        
        res1 = subprocess.run(cmd, capture_output=True, text=True)
        res2 = subprocess.run(cmd, capture_output=True, text=True)
        
        data1 = json.loads(res1.stdout)
        data2 = json.loads(res2.stdout)
        
        # Hash must be identical for same seed
        self.assertEqual(data1["scenario_set_hash"], data2["scenario_set_hash"])
        # Metrics must be identical
        self.assertEqual(data1["metrics"], data2["metrics"])

if __name__ == "__main__":
    unittest.main()