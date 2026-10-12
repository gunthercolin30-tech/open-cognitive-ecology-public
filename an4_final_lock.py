#!/usr/bin/env python3
from __future__ import annotations


def ready_inputs() -> dict:
    return {
        "synthetic": True,
        "axis": "AN",
        "step": "AN4",
    }


def main() -> None:
    from ontology.model_generator import ModelGenerator

    r = ModelGenerator().step(inputs=ready_inputs(), persist=False)

    assert r["model_generation_status"] == "AXIOMATIC_MODELS_GENERATED"
    assert r["axiomatic_models_generated"] is True
    assert r["axiom_count"] >= 10
    assert r["minimal_axiom_count"] >= 10
    assert r["model_count"] >= 3
    assert r["satisfying_model_count"] >= 2
    assert r["mean_model_axiom_coverage"] >= 0.95
    assert r["mean_model_consistency_score"] >= 0.90
    assert r["axiom_core_satisfiable"] is True
    assert r["ready_for_AN5_countermodel_generation"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True

    print("AN4_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
