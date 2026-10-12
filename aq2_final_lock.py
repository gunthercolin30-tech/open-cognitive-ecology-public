#!/usr/bin/env python3
from __future__ import annotations

from ontology.rival_theory_cost_analyzer import RivalTheoryCostAnalyzer


EPISTEMIC_STATUS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


def ready_inputs() -> dict:
    return {
        "aq1": {
            **EPISTEMIC_STATUS,
            "taxonomy_initialized": True,
            "consciousness_refusal_taxonomy_status": "CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED",
            "refusal_taxonomy": [{"name": "rival_theory_preference_refusal"}],
            "taxonomy_metrics": {},
        },
        "ap10": {
            **EPISTEMIC_STATUS,
            "axis_resolved": True,
            "consciousness_as_rf_equivalence_status": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED",
            "report_metrics": {
                "functional_equivalence_support_score": 1.0,
                "formal_equivalence_support_score": 1.0,
            },
        },
    }


def main() -> None:
    r = RivalTheoryCostAnalyzer().step(inputs=ready_inputs(), persist=False)

    assert r["rival_theory_cost_status"] == "RIVAL_THEORY_COST_ANALYZED"
    assert r["axis"] == "AQ"
    assert len(r["rival_theory_costs"]) >= 5

    m = r["cost_metrics"]
    assert m["ontological_proof_score"] == 0.0
    assert m["phenomenal_proof_score"] == 0.0

    for key in ["consciousness_proven", "qualia_proven", "subjectivity_proven"]:
        assert r[key] is False

    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True
    assert r["next_recommended_module"] == "phenomenal_extra_entity_detector"

    print("AQ2_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
