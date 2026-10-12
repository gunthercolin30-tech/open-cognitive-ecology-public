#!/usr/bin/env python3
from __future__ import annotations

from ontology.legacy_theory_failure_explainer import LegacyTheoryFailureExplainer


def ready_inputs() -> dict:
    return {
        "legacy_theory_failure_scores": {
            "iit": 0.82,
            "gwt": 0.84,
            "hot": 0.83,
            "predictive_processing": 0.81,
            "classical_functionalism": 0.86,
            "dualism": 0.90,
        },
        "legacy_theory_continuity_score": 0.86,
    }


def main() -> None:
    r = LegacyTheoryFailureExplainer().step(inputs=ready_inputs(), persist=False)
    assert r["legacy_theory_failure_status"] == "LEGACY_THEORY_FAILURES_EXPLAINED"
    assert r["public_schema_version"] == "AR4.legacy_theory_failure_explainer.v1"
    assert r["theory_count"] == 6
    assert r["incomplete_theory_count"] == 6
    assert r["all_legacy_theories_incomplete_under_rf_star_criteria"] is True
    assert r["mean_legacy_incompleteness_score"] >= 0.8
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    print("AR4_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
