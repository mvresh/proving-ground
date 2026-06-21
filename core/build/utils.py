import json
import hashlib

def to_canonical_json(data):
    """
    Serializes data to a JSON string with sorted keys and no whitespace.
    This ensures that the same data always results in the same byte sequence.
    """
    try:
        return json.dumps(data, sort_keys=True, separators=(',', ':'))
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize data to canonical JSON: {str(e)}")

def format_error(context, message):
    """Formats an error message for stderr."""
    return f"ERROR: [{context}] {message}"

def calculate_scenario_set_hash(scenario_set):
    """Calculates SHA-256 hex hash over canonical JSON of scenario set."""
    canonical = to_canonical_json(scenario_set)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()