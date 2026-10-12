#!/usr/bin/env python3
from __future__ import annotations


def ready_inputs() -> dict:
    return {
        "synthetic": True,
        "axis": "AN",
        "step": "AN3",
    }


def main() -> None:
    from ontology.axiom_minimality_analyzer import AxiomMinimalityAnalyzer

    r = AxiomMinimalityAnalyzer().step(inputs=ready_inputs(), persist=False)

    assert r["axiom_minimality_status"] == "AXIOM_MINIMALITY_ANALYZED"
    assert r["axiom_minimality_analyzed"] is True
    assert r["axiom_count"] >= 10
    assert r["axiom_minimality_score"] >= 0.70
    assert r["redundant_axiom_count"] == 0
    assert r["removable_axiom_count"] == 0
    assert r["axiom_set_functionally_minimal"] is True
    assert r["ready_for_AN4_model_generation"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True

    print("AN3_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
