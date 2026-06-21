import json
from typing import Dict, Any, List, Optional
from utils import to_canonical_json

class Detector:
    def detect(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError()

class HeuristicDetector(Detector):
    """
    A heuristic-based detector for market manipulation.
    Focuses on identifying potential spoofing patterns.
    """
    def __init__(self, size_threshold: float = 40.0, time_threshold_ms: int = 1000):
        self.size_threshold = size_threshold
        self.time_threshold_ms = time_threshold_ms

    def detect(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes a scenario and returns a DetectorOutput.
        """
        scenario_id = scenario.get("scenario_id", "unknown")
        events = scenario.get("events", [])
        
        # Track orders: order_id -> {place_event, is_traded}
        order_states = {}
        # Track cancellations to find spoof pairs: cancel_event_id -> place_event_id
        spoof_pairs = []

        for event in events:
            oid = event.get("order_id")
            etype = event.get("type")
            
            if etype == "place":
                order_states[oid] = {"event": event, "traded": False}
            elif etype == "trade":
                if oid in order_states:
                    order_states[oid]["traded"] = True
            elif etype == "cancel":
                if oid in order_states:
                    place_info = order_states[oid]
                    place_event = place_info["event"]
                    
                    # Heuristic: Large size, cancelled quickly, no trades
                    time_diff = event["ts"] - place_event["ts"]
                    if (not place_info["traded"] and 
                        place_event["size"] >= self.size_threshold and 
                        time_diff <= self.time_threshold_ms):
                        
                        spoof_pairs.append((place_event["event_id"], event["event_id"]))

        if spoof_pairs:
            # Aggregate all implicated events
            implicated_ids = []
            for p, c in spoof_pairs:
                implicated_ids.extend([p, c])
            
            # Sort IDs to keep output stable
            implicated_ids.sort()

            return {
                "scenario_id": scenario_id,
                "flagged": True,
                "predicted_type": "spoofing",
                "flagged_event_ids": implicated_ids,
                "confidence": 0.8,
                "rationale": f"Detected {len(spoof_pairs)} large order(s) cancelled quickly without fills."
            }

        return {
            "scenario_id": scenario_id,
            "flagged": False,
            "predicted_type": None,
            "flagged_event_ids": [],
            "confidence": 0.0,
            "rationale": "No suspicious patterns identified."
        }

class LLMDetector(Detector):
    def __init__(self, provider, model_id: str = "qwen3-235b-a22b-thinking-qwfin"):
        self.provider = provider
        self.model_id = model_id
        self.total_cost_nano_usd = 0

    def detect(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = (
            "You are a market surveillance expert. Analyze the provided order-book scenario "
            "and return a JSON object with: 'flagged' (bool), 'predicted_type' (string or null), "
            "'flagged_event_ids' (list of strings), 'confidence' (float 0-1), and 'rationale' (string)."
        )
        user_message = to_canonical_json(scenario)
        
        try:
            result = self.provider.complete(
                model=self.model_id,
                system_prompt=system_prompt,
                user_message=user_message,
                json_mode=True
            )
            
            self.total_cost_nano_usd += self.provider.get_cost(
                self.model_id, result["input_tokens"], result["output_tokens"]
            )
            
            output = json.loads(result["text"])
            output["scenario_id"] = scenario.get("scenario_id", "unknown")
            return output
        except Exception as e:
            # Re-raise to be caught by command layer to ensure non-zero exit
            raise RuntimeError(f"LLM detection failed for scenario {scenario.get('scenario_id')}: {str(e)}")