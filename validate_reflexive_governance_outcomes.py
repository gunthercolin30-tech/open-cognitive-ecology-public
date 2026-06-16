#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path.home() / "open-cognitive-ecology"
OUT = ROOT / "governance_outcome_validation_report.json"

def run_sequence(governance, values):
    results = []
    for v in values:
        results.append(
            governance.step(
                reflexive_threshold_result={"reflexive_coherence_score": v},
                constitutional_governance_score=v,
                longitudinal_result={"stability_index": v},
                inter_run_result={"inter_run_stability_index": v},
            )
        )
    return results

def stability_score(results):
    scores = [r["governance_activation_score"] for r in results]
    if not scores:
        return 1.0
    spread = max(scores) - min(scores)
    return max(0.0, min(1.0, 1.0 - spread))

def validate(results):
    return {
        "iterations": len(results),
        "stability_score": stability_score(results),
        "final_threshold": results[-1]["activation_threshold"],
        "final_effectiveness_score": results[-1].get("effectiveness_score", 0.0),
        "final_policy_bias": results[-1].get("policy_bias", 0.0),
    }

def main():
    from ontology.reflexive_threshold_governance import ReflexiveThresholdGovernance

    report = {
        "improving": validate(run_sequence(
            ReflexiveThresholdGovernance(),
            [0.40,0.45,0.50,0.55,0.60,0.70,0.80,0.90,0.95]
        )),
        "declining": validate(run_sequence(
            ReflexiveThresholdGovernance(),
            [0.95,0.90,0.80,0.70,0.60,0.55,0.50,0.45,0.40]
        )),
        "oscillation": validate(run_sequence(
            ReflexiveThresholdGovernance(),
            [0.95,0.40] * 10
        )),
        "stable": validate(run_sequence(
            ReflexiveThresholdGovernance(),
            [0.75] * 20
        )),
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    print("validation_report_saved=" + str(OUT))
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
