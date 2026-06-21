import sys
import json
import hashlib
from typing import Any, List, Dict
from generator import ScenarioGenerator, SpoofingInjector, ScenarioSetGenerator
from detector import HeuristicDetector, LLMDetector
from scorer import ScoringEngine
from utils import to_canonical_json
import llm_provider
import blob_store
from orchestrator import BenchmarkOrchestrator

def handle_attest(args: Any) -> str:
    input_data = sys.stdin.read()
    if not input_data.strip():
        raise ValueError("Empty input received on stdin")
    
    run_result = json.loads(input_data)
    if not isinstance(run_result, dict) or "run_id" not in run_result:
        raise ValueError("Input must be a valid RunResult JSON object")

    canonical_bytes = to_canonical_json(run_result).encode("utf-8")
    content_sha256 = hashlib.sha256(canonical_bytes).hexdigest()

    store = blob_store.get_blob_store(args.store)
    blob_id = store.store(canonical_bytes)

    attestation = {
        "run_id": run_result["run_id"],
        "scenario_set_hash": run_result["scenario_set_hash"],
        "store": args.store,
        "blob_id": blob_id,
        "content_sha256": content_sha256
    }
    return to_canonical_json(attestation)

def handle_verify(args: Any) -> str:
    input_data = sys.stdin.read()
    if not input_data.strip():
        raise ValueError("Empty input received on stdin")
    
    attestation = json.loads(input_data)
    required = ["blob_id", "content_sha256"]
    for field in required:
        if field not in attestation:
            raise ValueError(f"Attestation missing required field: {field}")

    blob_id = attestation["blob_id"]
    expected_sha256 = attestation["content_sha256"]
    
    store_name = getattr(args, "store", attestation.get("store", "stub"))
    store = blob_store.get_blob_store(store_name)
    
    fetched_bytes = store.fetch(blob_id)
    computed_sha256 = hashlib.sha256(fetched_bytes).hexdigest()
    
    verified = (computed_sha256 == expected_sha256)
    
    result = {
        "verified": verified,
        "blob_id": blob_id,
        "computed_sha256": computed_sha256,
        "expected_sha256": expected_sha256
    }
    
    output = to_canonical_json(result)
    if not verified:
        # We print first, then the command layer will handle the exit logic
        print(output)
        sys.exit(1)
    return output

def handle_models(args: Any) -> str:
    provider = llm_provider.get_provider(args.provider)
    models = provider.list_models()
    return to_canonical_json(models)

def handle_score(args: Any) -> str:
    input_data = sys.stdin.read()
    if not input_data.strip():
        raise ValueError("Empty input received on stdin")
    
    data = json.loads(input_data)
    if not isinstance(data, dict):
        raise ValueError("Input for 'score' must be a JSON object containing 'scenario_set' and 'detections'")
    
    scenario_set = data.get("scenario_set")
    detections = data.get("detections")
    
    if scenario_set is None or detections is None:
        raise ValueError("Input must contain 'scenario_set' and 'detections' keys")

    scorer = ScoringEngine()
    result = scorer.calculate_run_result(scenario_set, detections)
    return to_canonical_json(result)

def handle_detect(args: Any) -> str:
    input_data = sys.stdin.read()
    if not input_data.strip():
        raise ValueError("Empty input received on stdin")
    
    scenario_set = json.loads(input_data)
    if not isinstance(scenario_set, list):
        raise ValueError("Input for 'detect' must be a JSON array of scenarios")
        
    if args.detector == "llm":
        provider = llm_provider.get_provider(args.provider)
        model_id = "stub-detector-v1" if args.provider == "stub" else "qwen3-235b-a22b-thinking-qwfin"
        detector = LLMDetector(provider, model_id=model_id)
    else:
        detector = HeuristicDetector()

    results = [detector.detect(scn) for scn in scenario_set]
    return to_canonical_json(results)

def handle_generate_set(args: Any) -> str:
    generator = ScenarioSetGenerator(seed=args.seed)
    scenario_set = generator.generate_set(
        count=args.count,
        fraction=args.manipulated_fraction,
        market=args.market,
        events_per_scenario=args.events
    )
    return to_canonical_json(scenario_set)

def handle_generate(args: Any) -> str:
    generator = ScenarioGenerator(seed=args.seed)
    scenario = generator.generate_clean_scenario(
        market=args.market, 
        target_events=args.events
    )
    return to_canonical_json(scenario)

def handle_run(args: Any) -> str:
    run_result = BenchmarkOrchestrator.run_single_benchmark(args)
    return to_canonical_json(run_result)

def handle_inject(args: Any) -> str:
    input_data = sys.stdin.read()
    if not input_data.strip():
        raise ValueError("Empty input received on stdin")
    
    scenario = json.loads(input_data)
    injector = SpoofingInjector(seed=args.seed)
    manipulated = injector.inject_spoofing(scenario)
    return to_canonical_json(manipulated)

def handle_benchmark(args: Any) -> str:
    benchmark_result = BenchmarkOrchestrator.run_comparison_benchmark(args)
    return to_canonical_json(benchmark_result)