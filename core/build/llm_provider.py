import os
import json
import urllib.request
from typing import List, Dict, Any

class LLMProvider:
    def list_models(self) -> List[str]:
        raise NotImplementedError()

    def complete(self, model: str, system_prompt: str, user_message: str, json_mode: bool = False) -> Dict[str, Any]:
        """Returns {'text': str, 'input_tokens': int, 'output_tokens': int}"""
        raise NotImplementedError()

    def get_cost(self, model: str, input_tokens: int, output_tokens: int) -> int:
        raise NotImplementedError()

class StubProvider(LLMProvider):
    def list_models(self) -> List[str]:
        return ["stub-detector-v1", "stub-generator-v1"]

    def complete(self, model: str, system_prompt: str, user_message: str, json_mode: bool = False) -> Dict[str, Any]:
        # Deterministic stub logic: Flag if any order size >= 5 * median size
        try:
            scenario = json.loads(user_message)
            events = scenario.get("events", [])
            sizes = [e["size"] for e in events if "size" in e]
            
            flagged = False
            flagged_ids = []
            if sizes:
                sorted_sizes = sorted(sizes)
                mid = len(sorted_sizes) // 2
                median = (sorted_sizes[mid] + sorted_sizes[~mid]) / 2
                
                for e in events:
                    if e.get("type") == "place" and e.get("size", 0) >= 5 * median:
                        flagged = True
                        flagged_ids.append(e["event_id"])
            
            answer = {
                "flagged": flagged,
                "predicted_type": "spoofing" if flagged else None,
                "flagged_event_ids": flagged_ids,
                "confidence": 0.9 if flagged else 0.0,
                "rationale": "Stub logic based on median size multiplier."
            }
            return {
                "text": json.dumps(answer),
                "input_tokens": len(user_message) // 4,
                "output_tokens": len(json.dumps(answer)) // 4
            }
        except Exception:
            return {"text": "{}", "input_tokens": 0, "output_tokens": 0}

    def get_cost(self, model: str, input_tokens: int, output_tokens: int) -> int:
        return 0

class FlockProvider(LLMProvider):
    # Pricing from [resource]flock_pricing.json
    PRICING = {
        "qwen3-235b-a22b-thinking-qwfin": {"input": 230, "output": 2300},
        "qwen3-235b-a22b-thinking-2507": {"input": 230, "output": 2300},
        "qwen3-235b-a22b-instruct-2507": {"input": 700, "output": 2800},
        "qwen3-30b-a3b-instruct-2507": {"input": 200, "output": 800},
        "qwen3-30b-a3b-instruct-qmxai": {"input": 200, "output": 800},
        "kimi-k2-thinking": {"input": 600, "output": 2500},
        "deepseek-v3.2": {"input": 280, "output": 420},
        "minimax-m2.1": {"input": 300, "output": 1200}
    }

    def __init__(self):
        self.base_url = os.environ.get("FLOCK_BASE_URL", "https://api.flock.io/v1")
        self.api_key = os.environ.get("FLOCK_API_KEY")

    def list_models(self) -> List[str]:
        if not self.api_key:
            raise ValueError("FLOCK_API_KEY environment variable is not set. This is required for the 'flock' provider.")
        
        return self._request("GET", f"{self.base_url}/models")

    def complete(self, model: str, system_prompt: str, user_message: str, json_mode: bool = False) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("FLOCK_API_KEY environment variable is not set. This is required for the 'flock' provider.")

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        resp = self._request("POST", f"{self.base_url}/chat/completions", payload)
        
        return {
            "text": resp["choices"][0]["message"]["content"],
            "input_tokens": resp["usage"]["prompt_tokens"],
            "output_tokens": resp["usage"]["completion_tokens"]
        }

    def _request(self, method: str, url: str, data: Any = None) -> Any:
        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("x-litellm-api-key", self.api_key)
        req.add_header("Content-Type", "application/json")
        
        try:
            with urllib.request.urlopen(req) as response:
                resp_body = response.read().decode("utf-8")
                if response.status != 200:
                    raise RuntimeError(f"FLock API returned status {response.status}: {resp_body}")
                
                parsed = json.loads(resp_body)
                if method == "GET" and "/models" in url:
                    return sorted([m["id"] for m in parsed.get("data", [])])
                return parsed
        except urllib.error.URLError as e:
            raise RuntimeError(f"Network error connecting to FLock at {url}: {str(e)}")
        except Exception as e:
            if isinstance(e, (ValueError, RuntimeError)):
                raise e
            raise RuntimeError(f"Unexpected error calling FLock: {str(e)}")

    def get_cost(self, model: str, input_tokens: int, output_tokens: int) -> int:
        rates = self.PRICING.get(model)
        if not rates:
            return 0
        return (input_tokens * rates["input"]) + (output_tokens * rates["output"])

def get_provider(name: str) -> LLMProvider:
    if name == "stub":
        return StubProvider()
    elif name == "flock":
        return FlockProvider()
    else:
        raise ValueError(f"Unknown provider: {name}")