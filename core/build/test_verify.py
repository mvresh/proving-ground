import unittest
import json
import io
import sys
import hashlib
from unittest.mock import patch, MagicMock
import commands
from utils import to_canonical_json

class TestVerifyCommand(unittest.TestCase):
    def setUp(self):
        self.held_output = io.StringIO()
        self.held_err = io.StringIO()
        sys.stdout = self.held_output
        sys.stderr = self.held_err

    def tearDown(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def test_verify_success(self):
        """Test successful verification of an attestation."""
        content = b"test content"
        content_sha256 = hashlib.sha256(content).hexdigest()
        attestation = {
            "run_id": "run_123",
            "scenario_set_hash": "abc",
            "store": "stub",
            "blob_id": "stub_123",
            "content_sha256": content_sha256
        }
        
        mock_args = MagicMock()
        mock_args.store = "stub"
        
        mock_store = MagicMock()
        mock_store.fetch.return_value = content
        
        with patch('sys.stdin', io.StringIO(json.dumps(attestation))):
            with patch('blob_store.get_blob_store', return_value=mock_store):
                commands.cmd_verify(mock_args)
        
        output = json.loads(self.held_output.getvalue())
        self.assertTrue(output["verified"])
        self.assertEqual(output["computed_sha256"], content_sha256)

    def test_verify_tampered_fail(self):
        """Test verification failure when hashes do not match."""
        content = b"tampered content"
        expected_sha256 = "original_hash_that_wont_match"
        attestation = {
            "run_id": "run_123",
            "scenario_set_hash": "abc",
            "store": "stub",
            "blob_id": "stub_123",
            "content_sha256": expected_sha256
        }
        
        mock_args = MagicMock()
        mock_args.store = "stub"
        
        mock_store = MagicMock()
        mock_store.fetch.return_value = content
        
        with patch('sys.stdin', io.StringIO(json.dumps(attestation))):
            with patch('blob_store.get_blob_store', return_value=mock_store):
                with self.assertRaises(SystemExit) as cm:
                    commands.cmd_verify(mock_args)
                self.assertEqual(cm.exception.code, 1)
        
        output = json.loads(self.held_output.getvalue())
        self.assertFalse(output["verified"])
        self.assertNotEqual(output["computed_sha256"], expected_sha256)

    def test_verify_store_error(self):
        """Test handling of store fetch failures (hermetic)."""
        attestation = {
            "blob_id": "missing_blob",
            "content_sha256": "some_hash"
        }
        mock_args = MagicMock()
        mock_args.store = "stub"
        
        mock_store = MagicMock()
        mock_store.fetch.side_effect = RuntimeError("Blob not found")
        
        with patch('sys.stdin', io.StringIO(json.dumps(attestation))):
            with patch('blob_store.get_blob_store', return_value=mock_store):
                with self.assertRaises(SystemExit) as cm:
                    commands.cmd_verify(mock_args)
                self.assertEqual(cm.exception.code, 1)
        
        self.assertIn("ERROR: [VERIFY] Blob not found", self.held_err.getvalue())

if __name__ == "__main__":
    unittest.main()