import os
import hashlib
import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod

class BlobStore(ABC):
    @abstractmethod
    def store(self, blob_bytes: bytes) -> str:
        """Stores bytes and returns a blob_id."""
        pass

    @abstractmethod
    def fetch(self, blob_id: str) -> bytes:
        """Fetches bytes by blob_id."""
        pass

class StubBlobStore(BlobStore):
    def __init__(self, base_dir: str = ".pg_blobs"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def _get_id(self, blob_bytes: bytes) -> str:
        sha256 = hashlib.sha256(blob_bytes).hexdigest()
        return f"stub_{sha256}"

    def store(self, blob_bytes: bytes) -> str:
        blob_id = self._get_id(blob_bytes)
        path = os.path.join(self.base_dir, blob_id)
        with open(path, "wb") as f:
            f.write(blob_bytes)
        return blob_id

    def fetch(self, blob_id: str) -> bytes:
        path = os.path.join(self.base_dir, blob_id)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Blob {blob_id} not found in stub store")
        with open(path, "rb") as f:
            return f.read()

class WalrusBlobStore(BlobStore):
    def __init__(self):
        self.publisher = os.environ.get("WALRUS_PUBLISHER_URL", "https://publisher.walrus-testnet.walrus.space")
        self.aggregator = os.environ.get("WALRUS_AGGREGATOR_URL", "https://aggregator.walrus-testnet.walrus.space")
        self.user_agent = "ProvingGround/1.0"

    def store(self, blob_bytes: bytes) -> str:
        url = f"{self.publisher}/v1/blobs?epochs=5&deletable=false"
        req = urllib.request.Request(url, data=blob_bytes, method="PUT")
        req.add_header("User-Agent", self.user_agent)
        
        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                if "newlyCreated" in res_data:
                    return res_data["newlyCreated"]["blobObject"]["blobId"]
                elif "alreadyCertified" in res_data:
                    return res_data["alreadyCertified"]["blobId"]
                else:
                    raise ValueError(f"Unexpected Walrus response format: {res_data}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Walrus store failed: {str(e)}")

    def fetch(self, blob_id: str) -> bytes:
        url = f"{self.aggregator}/v1/blobs/{blob_id}"
        req = urllib.request.Request(url, method="GET")
        req.add_header("User-Agent", self.user_agent)
        
        try:
            with urllib.request.urlopen(req) as response:
                return response.read()
        except urllib.error.URLError as e:
            raise RuntimeError(f"Walrus fetch failed: {str(e)}")

def get_blob_store(name: str) -> BlobStore:
    if name == "stub":
        return StubBlobStore()
    elif name == "walrus":
        return WalrusBlobStore()
    else:
        raise ValueError(f"Unknown blob store: {name}")