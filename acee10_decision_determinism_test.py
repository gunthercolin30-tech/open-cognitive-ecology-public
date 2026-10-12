from __future__ import annotations
from copy import deepcopy
from ontology.acee_selection_policy import AceeSelectionPolicy

BASE = {
    "selection_id": "determinism-case",
    "timestamp_utc": "2026-07-13T20:00:00Z",
    "impact_evaluation": {
        "comparison_valid": True,
        "impact_score": 0.12,
        "metric_classifications": {"closure_pressure": "unchanged"},
    },
    "causal_analysis": {
        "ready_for_selection": True,
        "causal_effect_resolved": True,
        "causal_probability": 0.90,
        "causal_confidence": 0.90,
        "effect_size": 0.12,
        "effect_direction": "beneficial",
    },
    "stability_evidence": {"stability_score": 0.90},
    "simplicity_evidence": {"simplicity_score": 0.80},
    "reversibility_evidence": {
        "mean_reversibility_score": 0.90,
        "reversibility_assured": True,
    },
    "non_closure_evidence": {
        "closure_pressure": 0.10,
        "non_closure_score": 0.90,
    },
    "constitutional_evidence": {
        "compliant": True,
        "constitutional_compliance_score": 0.90,
    },
    "governance_evidence": {
        "approved": True,
        "governance_score": 0.90,
    },
}

STABLE_FIELDS = (
    "selection_status", "selection_decision_ready", "decision",
    "decision_reasons", "vetoes", "blocking_reasons", "impact_score",
    "causal_probability", "causal_confidence", "effect_size",
    "effect_direction", "stability_score", "simplicity_score",
    "reversibility_score", "reversibility_assured", "closure_pressure",
    "closure_pressure_increased", "constitutional_compliant",
    "governance_approved", "acceptance_authorized", "rollback_requested",
    "rollback_request", "rollback_executed", "acee11_called",
    "selection_hash",
)

def projection(result):
    return {key: result[key] for key in STABLE_FIELDS}

def main() -> None:
    policy = AceeSelectionPolicy()
    baseline = policy.step(inputs=deepcopy(BASE), persist=False)
    expected = projection(baseline)
    assert baseline["decision"] == "accept"
    assert baseline["selection_decision_ready"] is True
    for _ in range(100):
        result = policy.step(inputs=deepcopy(BASE), persist=False)
        assert projection(result) == expected
    print("ACEE10_DECISION_DETERMINISM_OK")

if __name__ == "__main__":
    main()
