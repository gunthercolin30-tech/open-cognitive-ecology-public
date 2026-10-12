#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = "best_explanation_status_resolver"
COMMON = {"consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False, "phenomenology_undetermined": True, "functional_conclusion_only": True}

def synthetic_inputs() -> dict[str, Any]:
    aq6_metrics = {"mean_anti_rf_refusal_cost_score": 0.84, "mean_countermodel_viability_score": 0.18, "low_viability_countermodel_ratio": 0.92, "mean_support_deficit_score": 0.86, "dependency_resolution_score": 1.0, "ontological_proof_score": 0.0, "phenomenal_proof_score": 0.0, "consciousness_proof_score": 0.0}
    return {
        "aq1": {**COMMON, "consciousness_refusal_taxonomy_status": "CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED", "taxonomy_initialized": True, "refusal_taxonomy": [{"id": i} for i in range(8)]},
        "aq2": {**COMMON, "rival_theory_cost_status": "RIVAL_THEORY_COST_ANALYZED", "cost_analysis_completed": True, "rival_theory_costs": [{"rival_theory": "Dualism", "refusal_cost_score": 0.88}]},
        "aq3": {**COMMON, "phenomenal_extra_entity_status": "PHENOMENAL_EXTRA_ENTITIES_DETECTED", "extra_entity_detection_completed": True, "phenomenal_extra_entities": [{"rival_theory": "Dualism", "extra_entity_burden_score": 0.89}]},
        "aq4": {**COMMON, "no_difference_penalty_status": "NO_DIFFERENCE_PENALTY_CHECKED", "penalty_check_completed": True, "no_difference_penalties": [{"rival_theory": "Dualism", "no_difference_penalty_score": 0.86}]},
        "aq5": {**COMMON, "minimal_property_denial_status": "MINIMAL_PROPERTY_DENIAL_CHECKED", "denial_check_completed": True, "minimal_property_denials": [{"rival_theory": "Eliminativism", "minimal_property_denial_cost_score": 0.91}]},
        "aq6": {**COMMON, "anti_rf_countermodel_status": "ANTI_RF_COUNTERMODELS_EVALUATED", "countermodel_evaluation_completed": True, "anti_rf_countermodels": [{"countermodel_id": "ARF1"}], "countermodel_metrics": aq6_metrics},
        "ap10": {**COMMON, "consciousness_as_rf_equivalence_status": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED", "axis_resolved": True},
    }

def assert_numeric_bounds(metrics: dict[str, Any]) -> None:
    for k, v in metrics.items():
        if isinstance(v, (int, float)):
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
    assert "anti_rf_countermodel_evaluator" in dependency_registry.DEPENDENCY_REGISTRY[MODULE]
    py_compile.compile(str(ROOT / "ontology" / f"{MODULE}.py"), cfile="/private/tmp/aq7_best_explanation_status_resolver.pyc", doraise=True)

def main() -> None:
    import sys
    sys.path.insert(0, str(ROOT))
    from ontology.best_explanation_status_resolver import BestExplanationStatusResolver
    inputs = synthetic_inputs()
    r = BestExplanationStatusResolver().step(inputs=inputs, persist=False)
    assert r["best_explanation_status"] == "BEST_EXPLANATION_STATUS_RESOLVED"
    assert r["functional_best_explanation_resolution"] == "RF_STAR_CURRENTLY_BEST_FUNCTIONAL_EXPLANATION"
    assert r["best_explanation_completed"] is True
    assert r["step"] == "AQ7" and r["axis"] == "AQ"
    assert r["public_schema_version"] == "AQ7.best_explanation_status_resolver.v1"
    assert len(r["resolution_arguments"]) >= 4
    assert_numeric_bounds(r["best_explanation_metrics"])
    m = r["best_explanation_metrics"]
    assert m["dependency_resolution_score"] == 1.0
    assert m["rf_explanatory_support_score"] > m["rival_explanatory_support_score"]
    assert m["ontological_proof_score"] == 0.0 and m["phenomenal_proof_score"] == 0.0 and m["consciousness_proof_score"] == 0.0
    for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven"]:
        assert r[k] is False
    assert r["phenomenology_undetermined"] is True and r["functional_conclusion_only"] is True
    assert r["next_recommended_module"] == "refusal_cost_reporter"
    r2 = BestExplanationStatusResolver().step(inputs=inputs, persist=False)
    volatile = {"timestamp_utc", "persistence"}
    assert {k: v for k, v in r.items() if k not in volatile} == {k: v for k, v in r2.items() if k not in volatile}
    persisted = BestExplanationStatusResolver().step(inputs=inputs, persist=True)
    assert_persistence(persisted)
    assert_inventory_and_registry()
    print("AQ7_FAST_ACCEPTANCE_OK")

if __name__ == "__main__":
    main()
