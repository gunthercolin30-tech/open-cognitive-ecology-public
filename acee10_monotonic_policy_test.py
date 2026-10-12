from __future__ import annotations
from copy import deepcopy
from ontology.acee_selection_policy import AceeSelectionPolicy

BASE = {
    "selection_id": "monotonic-policy-case",
    "timestamp_utc": "2026-07-13T20:00:00Z",
    "impact_evaluation": {
        "comparison_valid": True,
        "impact_score": 0.12,
        "metric_classifications": {"closure_pressure": "unchanged"},
    },
    "causal_analysis": {
        "ready_for_selection": True,
        "causal_effect_resolved": True,
        "causal_probability": 0.50,
        "causal_confidence": 0.50,
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

DECISION_RANK = {"repeat": 0, "sandbox_longer": 1, "accept": 2}

def main() -> None:
    policy = AceeSelectionPolicy()
    decisions = []
    for integer_confidence in range(50, 100):
        confidence = integer_confidence / 100.0
        case = deepcopy(BASE)
        case["causal_analysis"]["causal_confidence"] = confidence
        case["causal_analysis"]["causal_probability"] = confidence
        result = policy.step(inputs=case, persist=False)
        decision = result["decision"]
        assert decision in DECISION_RANK
        assert result["rollback_requested"] is False
        assert result["rollback_executed"] is False
        assert result["acee11_called"] is False
        decisions.append(decision)

    ranks = [DECISION_RANK[item] for item in decisions]
    assert ranks == sorted(ranks)
    assert decisions[0] == "sandbox_longer"
    assert decisions[-1] == "accept"
    assert sum(a != b for a, b in zip(decisions, decisions[1:])) == 1
    first_accept = decisions.index("accept")
    assert first_accept == 10
    assert all(item == "sandbox_longer" for item in decisions[:first_accept])
    assert all(item == "accept" for item in decisions[first_accept:])
    print("ACEE10_MONOTONIC_POLICY_OK")

if __name__ == "__main__":
    main()
