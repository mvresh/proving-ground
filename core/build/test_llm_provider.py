import unittest
import os
import json
import urllib.error
from unittest.mock import patch, MagicMock
from llm_provider import StubProvider, FlockProvider, get_provider

class TestLLMProviders(unittest.TestCase):
    def test_stub_provider_determinism(self):
        provider = StubProvider()
        models = provider.list_models()
        self.assertEqual(models, ["stub-detector-v1", "stub-generator-v1"])
        self.assertEqual(models, provider.list_models())
        self.assertEqual(provider.get_cost("any", 100, 100), 0)

    @patch("urllib.request.urlopen")
    def test_flock_provider_success(self, mock_urlopen):
        # Mock response for /v1/models
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({
            "data": [{"id": "model-b"}, {"id": "model-a"}]
        }).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        with patch.dict(os.environ, {"FLOCK_API_KEY": "test-key"}):
            provider = FlockProvider()
            models = provider.list_models()
            # Test sorting and extraction
            self.assertEqual(models, ["model-a", "model-b"])
            
            # Verify headers
            args, kwargs = mock_urlopen.call_args
            req = args[0]
            self.assertEqual(req.get_header("X-litellm-api-key"), "test-key")

    def test_flock_provider_missing_key(self):
        with patch.dict(os.environ, {}, clear=True):
            provider = FlockProvider()
            with self.assertRaises(ValueError) as cm:
                provider.list_models()
            self.assertIn("FLOCK_API_KEY", str(cm.exception))

    @patch("urllib.request.urlopen")
    def test_flock_provider_http_error(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.read.return_value = b"Internal Server Error"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        with patch.dict(os.environ, {"FLOCK_API_KEY": "test-key"}):
            provider = FlockProvider()
            with self.assertRaises(RuntimeError) as cm:
                provider.list_models()
            self.assertIn("500", str(cm.exception))
            self.assertIn("Internal Server Error", str(cm.exception))

    def test_flock_pricing_logic(self):
        provider = FlockProvider()
        # Test known model from [resource]flock_pricing.json: 
        # deepseek-v3.2 -> input: 280, output: 420
        # 100 input * 280 + 50 output * 420 = 28000 + 21000 = 49000
        cost = provider.get_cost("deepseek-v3.2", 100, 50)
        self.assertEqual(cost, 49000)

        # Test unknown model returns 0
        self.assertEqual(provider.get_cost("unknown-model", 100, 100), 0)

    def test_get_provider_factory(self):
        self.assertIsInstance(get_provider("stub"), StubProvider)
        self.assertIsInstance(get_provider("flock"), FlockProvider)
        with self.assertRaises(ValueError):
            get_provider("invalid")

if __name__ == "__main__":
    unittest.main()