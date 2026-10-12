#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = "minimal_property_denial_checker"


def synthetic_inputs() -> dict[str, Any]:
    common = {"consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False, "phenomenology_undetermined": True, "functional_conclusion_only": True}
    return {
        "aq1": {**common, "consciousness_refusal_taxonomy_status": "CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED", "taxonomy_initialized": True, "refusal_taxonomy": [{"id": i} for i in range(8)]},
        "aq2": {**common, "rival_theory_cost_status": "RIVAL_THEORY_COST_ANALYZED", "cost_analysis_completed": True, "rival_theory_costs": [{"rival_theory": "Dualism", "refusal_cost_score": 0.9}]},
        "aq3": {**common, "phenomenal_extra_entity_status": "PHENOMENAL_EXTRA_ENTITIES_DETECTED", "extra_entity_detection_completed": True, "phenomenal_extra_entities": [{"rival_theory": "Dualism", "extra_entity_burden_score": 0.9}]},
        "aq4": {**common, "no_difference_penalty_status": "NO_DIFFERENCE_PENALTY_CHECKED", "penalty_check_completed": True, "no_difference_penalties": [{"rival_theory": "Dualism", "no_difference_penalty_score": 0.9}]},
        "ap1": {**common, "consciousness_minimal_properties_status": "CONSCIOUSNESS_MINIMAL_PROPERTIES_REGISTERED", "minimal_properties_registered": True, "minimal_properties": [{"name": "unity"}]},
        "ap3": {**common, "consciousness_rf_property_mapping_status": "CONSCIOUSNESS_RF_PROPERTY_MAPPING_COMPLETED", "property_mapping_completed": True},
        "ap10": {**common, "consciousness_as_rf_equivalence_status": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED", "axis_resolved": True},
    }


def assert_numeric_bounds(metrics: dict[str, Any]) -> None:
    for k, v in metrics.items():
        assert isinstance(v, (int, float)), k
        assert 0.0 <= float(v) <= 1.0, k


def assert_persistence(r: dict[str, Any]) -> None:
    p = r["persistence"]
    for key in ["latest_json_path", "latest_markdown_path", "latest_prometheus_path", "history_path"]:
        assert Path(p[key]).exists(), key


def assert_inventory_and_registry() -> None:
    for f in ["ontology_inventory.txt", "ontology_inventory.py", "ontology/ontology_inventory.py", "global_module_catalog.txt", "global_module_catalog.py"]:
        assert MODULE in (ROOT / f).read_text(encoding="utf-8"), f
    import dependency_registry
    assert MODULE in dependency_registry.DEPENDENCY_REGISTRY, MODULE
    assert "no_difference_penalty_checker" in dependency_registry.DEPENDENCY_REGISTRY[MODULE]
    py_compile.compile(str(ROOT / "ontology" / f"{MODULE}.py"), cfile="/private/tmp/aq5_minimal_property_denial_checker.pyc", doraise=True)


def main() -> None:
    import sys
    sys.path.insert(0, str(ROOT))
    from ontology.minimal_property_denial_checker import MinimalPropertyDenialChecker

    inputs = synthetic_inputs()
    r = MinimalPropertyDenialChecker().step(inputs=inputs, persist=False)
    assert r["minimal_property_denial_status"] == "MINIMAL_PROPERTY_DENIAL_CHECKED"
    assert r["denial_check_completed"] is True
    assert r["step"] == "AQ5"
    assert r["axis"] == "AQ"
    assert r["public_schema_version"] == "AQ5.minimal_property_denial_checker.v1"
    assert len(r["recovered_minimal_properties"]) >= 9
    assert len(r["minimal_property_denials"]) >= 7
    for item in r["minimal_property_denials"]:
        assert 0.0 <= item["minimal_property_denial_cost_score"] <= 1.0
        assert item["denial_cost_classification"] in {"low_property_denial_cost", "moderate_property_denial_cost", "high_property_denial_cost", "severe_property_denial_cost"}
    assert_numeric_bounds(r["denial_metrics"])
    assert r["denial_metrics"]["ontological_proof_score"] == 0.0
    assert r["denial_metrics"]["phenomenal_proof_score"] == 0.0
    assert r["denial_metrics"]["consciousness_proof_score"] == 0.0
    for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven"]:
        assert r[k] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True
    assert r["next_recommended_module"] == "anti_rf_countermodel_evaluator"
    r2 = MinimalPropertyDenialChecker().step(inputs=inputs, persist=False)
    volatile = {"timestamp_utc", "persistence"}
    assert {k: v for k, v in r.items() if k not in volatile} == {k: v for k, v in r2.items() if k not in volatile}
    persisted = MinimalPropertyDenialChecker().step(inputs=inputs, persist=True)
    assert_persistence(persisted)
    assert_inventory_and_registry()
    print("AQ5_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
