from typing import List, Dict, Any

class ScoringEngine:
    """
    Computes metrics and identifies misses by comparing detector outputs 
    against the ground truth in scenarios.
    """
    
    def calculate_run_result(self, scenario_set: List[Dict[str, Any]], detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(scenario_set) != len(detections):
            raise ValueError(
                f"Input mismatch: scenario_set has {len(scenario_set)} items, "
                f"but detections has {len(detections)} items."
            )

        tp = 0  # True Positives
        fp = 0  # False Positives
        tn = 0  # True Negatives
        fn = 0  # False Negatives
        
        # breakdown for spoofing
        spoof_caught = 0
        spoof_total = 0
        
        misses = []

        for scn, det in zip(scenario_set, detections):
            if scn["scenario_id"] != det["scenario_id"]:
                raise ValueError(
                    f"ID mismatch: Expected scenario {scn['scenario_id']}, "
                    f"but detector output provided {det['scenario_id']}"
                )

            gt = scn["ground_truth"]
            is_manipulated = gt["label"] == "manipulated"
            is_flagged = det["flagged"]
            m_type = gt.get("manipulation_type")

            if is_manipulated:
                if m_type == "spoofing":
                    spoof_total += 1
                
                if is_flagged:
                    tp += 1
                    if m_type == "spoofing":
                        spoof_caught += 1
                else:
                    fn += 1
                    misses.append({
                        "scenario_id": scn["scenario_id"],
                        "manipulation_type": m_type,
                        "explanation": gt["explanation"]
                    })
            else:
                if is_flagged:
                    fp += 1
                else:
                    tn += 1

        catch_rate = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

        return {
            "metrics": {
                "catch_rate": catch_rate,
                "false_positive_rate": fpr,
                "precision": precision,
                "by_type": {
                    "spoofing": {
                        "caught": spoof_caught,
                        "total": spoof_total
                    }
                }
            },
            "misses": misses
        }