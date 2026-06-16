#!/usr/bin/env python3
from ontology.reflexive_threshold_governance import ReflexiveThresholdGovernance
import json

def run(values):
    g = ReflexiveThresholdGovernance()
    results = []

    for v in values:
        r = g.step(
            reflexive_threshold_result={
                "reflexive_coherence_score": v
            },
            constitutional_governance_score=v,
            longitudinal_result={
                "stability_index": v
            },
            inter_run_result={
                "inter_run_stability_index": v
            }
        )

        results.append({
            "input_score": v,
            "effectiveness_score": r.get("effectiveness_score"),
            "effectiveness_delta": r.get("effectiveness_delta"),
            "meta_policy_gain": r.get("meta_policy_gain"),
            "policy_bias": r.get("policy_bias"),
        })

    return results

report = {
    "improving": run([0.40,0.45,0.50,0.55,0.60,0.70,0.80,0.90,0.95]),
    "declining": run([0.95,0.90,0.80,0.70,0.60,0.55,0.50,0.45,0.40]),
    "oscillation": run([0.95,0.40] * 10),
    "stable": run([0.75] * 20),
}

print(json.dumps(report, indent=2))
