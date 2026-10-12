#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent


def ready_inputs() -> dict:
    return {
        "synthetic": True,
        "axis": "AN",
        "step": "AN1",
        "extra_axioms": [],
    }


def main() -> None:
    from ontology.axiom_registry import AxiomRegistry

    r = AxiomRegistry().step(inputs=ready_inputs(), persist=False)

    assert r["axiom_registry_status"] == "AXIOM_REGISTRY_ESTABLISHED"
    assert r["axiom_registry_established"] is True
    assert r["axiomatic_completeness_status"] == "AN1_REGISTRY_READY"
    assert r["ready_for_AN2_independence_testing"] is True
    assert r["axiom_count"] >= 10
    assert r["registry_completeness_score"] >= 0.99
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True

    print("AN1_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
