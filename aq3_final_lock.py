#!/usr/bin/env python3
from __future__ import annotations

from ontology.phenomenal_extra_entity_detector import PhenomenalExtraEntityDetector


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
            "refusal_taxonomy": [{"name": "phenomenal_extra_entity_refusal"}],
            "taxonomy_metrics": {},
        },
        "aq2": {
            **EPISTEMIC_STATUS,
            "cost_analysis_completed": True,
            "rival_theory_cost_status": "RIVAL_THEORY_COST_ANALYZED",
            "rival_theory_costs": [
                {
                    "name": "Dualism",
                    "refusal_cost_score": 0.9,
                    "extra_entity_requirement": 0.96,
                    "measurement_gap_cost": 0.88,
                }
            ],
            "cost_metrics": {
                "ontological_proof_score": 0.0,
                "phenomenal_proof_score": 0.0,
            },
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
    r = PhenomenalExtraEntityDetector().step(inputs=ready_inputs(), persist=False)

    assert r["phenomenal_extra_entity_status"] == "PHENOMENAL_EXTRA_ENTITIES_DETECTED"
    assert r["extra_entity_detection_completed"] is True
    assert r["step"] == "AQ3"
    assert r["axis"] == "AQ"
    assert len(r["phenomenal_extra_entities"]) >= 7

    m = r["extra_entity_metrics"]
    assert m["ontological_proof_score"] == 0.0
    assert m["phenomenal_proof_score"] == 0.0
    assert m["phenomenal_entity_proof_score"] == 0.0

    for key in ["consciousness_proven", "qualia_proven", "subjectivity_proven"]:
        assert r[key] is False

    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True
    assert r["next_recommended_module"] == "no_difference_penalty_checker"

    print("AQ3_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
