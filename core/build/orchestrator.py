import secrets
import datetime
from typing import Any, Dict, List
from generator import ScenarioSetGenerator
from detector import HeuristicDetector, LLMDetector
from scorer import ScoringEngine
import llm_provider
from utils import calculate_scenario_set_hash

class BenchmarkOrchestrator:
    """
    Orchestrates complex flows involving multiple components (generation, detection, scoring).
    """

    @staticmethod
    def run_single_benchmark(args: Any) -> Dict[str, Any]:
        """Orchestrates a single detector run."""
        generator = ScenarioSetGenerator(seed=args.seed)
        scenario_set = generator.generate_set(
            count=args.count,
            fraction=args.manipulated_fraction,
            market=args.market,
            events_per_scenario=args.events
        )
        
        scenario_set_hash = calculate_scenario_set_hash(scenario_set)
        
        # In the current 'run' command requirement, it uses HeuristicDetector
        detector = HeuristicDetector()
        detections = [detector.detect(scn) for scn in scenario_set]
        
        scorer = ScoringEngine()
        score_result = scorer.calculate_run_result(scenario_set, detections)
        
        run_id = f"run_{secrets.token_hex(8)}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace("+00:00", "Z")
        
        return {
            "run_id": run_id,
            "detector_id": args.detector_id,
            "timestamp": timestamp,
            "scenario_set_hash": scenario_set_hash,
            "metrics": score_result["metrics"],
            "misses": score_result["misses"],
            "walrus_blob_id": None,
            "sui_object_id": None
        }

    @staticmethod
    def run_comparison_benchmark(args: Any) -> Dict[str, Any]:
        """Orchestrates a comparison between Heuristic and LLM detectors."""
        generator = ScenarioSetGenerator(seed=args.seed)
        scenario_set = generator.generate_set(
            count=args.count,
            fraction=args.manipulated_fraction,
            market=args.market,
            events_per_scenario=args.events
        )
        
        scenario_set_hash = calculate_scenario_set_hash(scenario_set)
        
        h_detector = HeuristicDetector()
        provider = llm_provider.get_provider(args.provider)
        model_id = "stub-detector-v1" if args.provider == "stub" else "qwen3-235b-a22b-thinking-qwfin"
        l_detector = LLMDetector(provider, model_id=model_id)
        
        h_detections = [h_detector.detect(scn) for scn in scenario_set]
        l_detections = [l_detector.detect(scn) for scn in scenario_set]
        
        scorer = ScoringEngine()
        h_score = scorer.calculate_run_result(scenario_set, h_detections)
        l_score = scorer.calculate_run_result(scenario_set, l_detections)
        
        return {
            "scenario_set_hash": scenario_set_hash,
            "detectors": [
                {
                    "detector_id": "heuristic_v1",
                    "metrics": h_score["metrics"],
                    "misses": h_score["misses"]
                },
                {
                    "detector_id": "llm_v1",
                    "metrics": l_score["metrics"],
                    "misses": l_score["misses"]
                }
            ],
            "cost_nano_usd": l_detector.total_cost_nano_usd
        }