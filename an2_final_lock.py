#!/usr/bin/env python3
from __future__ import annotations


def ready_inputs() -> dict:
    return {
        "synthetic": True,
        "axis": "AN",
        "step": "AN2",
    }


def main() -> None:
    from ontology.axiom_independence_tester import AxiomIndependenceTester

    r = AxiomIndependenceTester().step(inputs=ready_inputs(), persist=False)

    assert r["axiom_independence_status"] == "AXIOM_INDEPENDENCE_TESTED"
    assert r["axiom_independence_tested"] is True
    assert r["axiom_count"] >= 10
    assert r["mean_axiom_independence_score"] >= 0.70
    assert r["potentially_derivable_axiom_count"] == 0
    assert r["circular_dependency_count"] == 0
    assert r["ready_for_AN3_minimality_analysis"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True

    print("AN2_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
