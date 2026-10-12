#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = "consciousness_refusal_taxonomy"
EPISTEMIC_STATUS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


def ready_aq1_inputs() -> dict[str, Any]:
    base = dict(EPISTEMIC_STATUS)
    return {
        "ap10": dict(
            base,
            axis_resolved=True,
            consciousness_as_rf_equivalence_status="CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED",
            report_metrics={
                "functional_equivalence_support_score": 1.0,
                "formal_equivalence_support_score": 1.0,
            },
        ),
        "ap9": dict(
            base,
            status_resolved=True,
            status_metrics={
                "functional_support_score": 1.0,
                "formal_support_score": 1.0,
            },
        ),
    }


def assert_epistemic_guards(r: dict[str, Any]) -> None:
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True
    assert r["epistemic_status"]["consciousness_proven"] is False
    assert r["epistemic_status"]["qualia_proven"] is False
    assert r["epistemic_status"]["subjectivity_proven"] is False
    assert r["epistemic_status"]["phenomenology_undetermined"] is True


def assert_numeric_bounds(metrics: dict[str, Any]) -> None:
    for k, v in metrics.items():
        assert isinstance(v, (int, float)), k
        assert 0.0 <= float(v) <= 1.0, k


def assert_persistence(r: dict[str, Any]) -> None:
    p = r["persistence"]
    for key in ["latest_json_path", "latest_markdown_path", "latest_prometheus_path", "history_path"]:
        assert Path(p[key]).exists(), key


def assert_inventory_and_registry() -> None:
    for f in [
        "ontology_inventory.txt",
        "ontology_inventory.py",
        "ontology/ontology_inventory.py",
        "global_module_catalog.txt",
        "global_module_catalog.py",
    ]:
        assert MODULE in (ROOT / f).read_text(encoding="utf-8"), f
    import dependency_registry
    assert MODULE in dependency_registry.DEPENDENCY_REGISTRY, MODULE
    py_compile.compile(
        str(ROOT / "ontology" / f"{MODULE}.py"),
        cfile=str(Path("/private/tmp") / f"oce_{MODULE}.pyc"),
        doraise=True,
    )


def main() -> None:
    import sys
    sys.path.insert(0, str(ROOT))
    from ontology.consciousness_refusal_taxonomy import ConsciousnessRefusalTaxonomy

    r = ConsciousnessRefusalTaxonomy().step(inputs=ready_aq1_inputs(), persist=False)
    assert r["consciousness_refusal_taxonomy_status"] == "CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED"
    assert r["taxonomy_initialized"] is True
    assert r["step"] == "AQ1"
    assert r["axis"] == "AQ"
    assert r["public_schema_version"] == "AQ1.consciousness_refusal_taxonomy.v1"
    assert r["ap_dependency_status"] == "AP_RESOLVED"
    assert len(r["refusal_taxonomy"]) >= 8
    assert {x["name"] for x in r["refusal_taxonomy"]} >= {
        "empirical_evidence_refusal",
        "phenomenal_extra_entity_refusal",
        "no_difference_refusal",
        "minimal_property_denial_refusal",
        "anti_rf_countermodel_refusal",
        "rival_theory_preference_refusal",
    }
    assert_numeric_bounds(r["taxonomy_metrics"])
    assert r["taxonomy_metrics"]["ontological_proof_score"] == 0.0
    assert r["taxonomy_metrics"]["phenomenal_proof_score"] == 0.0
    assert_epistemic_guards(r)
    assert r["next_recommended_module"] == "rival_theory_cost_analyzer"

    a = ConsciousnessRefusalTaxonomy().step(inputs=ready_aq1_inputs(), persist=False)
    b = ConsciousnessRefusalTaxonomy().step(inputs=ready_aq1_inputs(), persist=False)
    assert a["refusal_taxonomy"] == b["refusal_taxonomy"]
    assert a["taxonomy_metrics"] == b["taxonomy_metrics"]

    degraded_inputs = ready_aq1_inputs()
    degraded_inputs["ap10"] = dict(EPISTEMIC_STATUS, axis_resolved=False, report_metrics={})
    degraded = ConsciousnessRefusalTaxonomy().step(inputs=degraded_inputs, persist=False)
    assert degraded["consciousness_refusal_taxonomy_status"] == "CONSCIOUSNESS_REFUSAL_TAXONOMY_INCOMPLETE"
    assert degraded["taxonomy_initialized"] is False
    assert degraded["consciousness_proven"] is False
    assert degraded["phenomenology_undetermined"] is True

    persisted = ConsciousnessRefusalTaxonomy().step(inputs=ready_aq1_inputs(), persist=True)
    assert_persistence(persisted)
    assert_inventory_and_registry()
    print("AQ1_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
