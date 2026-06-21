import unittest
from unittest.mock import patch, MagicMock
import blob_store
import json
import io

class TestBlobStore(unittest.TestCase):
    def test_stub_store_determinism(self):
        store = blob_store.StubBlobStore(base_dir=".test_blobs")
        data = b"hello world"
        id1 = store.store(data)
        id2 = store.store(data)
        self.assertEqual(id1, id2)
        self.assertTrue(id1.startswith("stub_"))
        
        fetched = store.fetch(id1)
        self.assertEqual(fetched, data)

    @patch("urllib.request.urlopen")
    def test_walrus_store_newly_created(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "newlyCreated": {"blobObject": {"blobId": "walrus_abc_123"}}
        }).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        store = blob_store.WalrusBlobStore()
        blob_id = store.store(b"some data")
        self.assertEqual(blob_id, "walrus_abc_123")

    @patch("urllib.request.urlopen")
    def test_walrus_store_already_certified(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "alreadyCertified": {"blobId": "walrus_existing_456"}
        }).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        store = blob_store.WalrusBlobStore()
        blob_id = store.store(b"some data")
        self.assertEqual(blob_id, "walrus_existing_456")

    @patch("urllib.request.urlopen")
    def test_walrus_store_error(self, mock_urlopen):
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Network Down")
        
        store = blob_store.WalrusBlobStore()
        with self.assertRaisesRegex(RuntimeError, "Walrus store failed"):
            store.store(b"data")

if __name__ == "__main__":
    unittest.main()