#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = "phenomenal_extra_entity_detector"
EPISTEMIC_STATUS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


def ready_aq3_inputs() -> dict[str, Any]:
    base = dict(EPISTEMIC_STATUS)
    rival_theory_costs = [
        {
            "name": "Dualism",
            "refusal_cost_score": 0.9,
            "extra_entity_requirement": 0.96,
            "measurement_gap_cost": 0.88,
        },
        {
            "name": "IIT",
            "refusal_cost_score": 0.55,
            "extra_entity_requirement": 0.36,
            "measurement_gap_cost": 0.38,
        },
    ]
    return {
        "aq1": dict(
            base,
            taxonomy_initialized=True,
            consciousness_refusal_taxonomy_status="CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED",
            refusal_taxonomy=[{"name": "phenomenal_extra_entity_refusal"}],
            taxonomy_metrics={},
        ),
        "aq2": dict(
            base,
            cost_analysis_completed=True,
            rival_theory_cost_status="RIVAL_THEORY_COST_ANALYZED",
            rival_theory_costs=rival_theory_costs,
            cost_metrics={
                "ontological_proof_score": 0.0,
                "phenomenal_proof_score": 0.0,
            },
        ),
        "ap10": dict(
            base,
            axis_resolved=True,
            consciousness_as_rf_equivalence_status="CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED",
            report_metrics={
                "functional_equivalence_support_score": 1.0,
                "formal_equivalence_support_score": 1.0,
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
    assert r["epistemic_status"]["phenomenal_entity_proven"] is False


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
    assert "rival_theory_cost_analyzer" in dependency_registry.DEPENDENCY_REGISTRY[MODULE]
    py_compile.compile(
        str(ROOT / "ontology" / f"{MODULE}.py"),
        cfile=str(Path("/private/tmp") / f"oce_{MODULE}.pyc"),
        doraise=True,
    )


def main() -> None:
    import sys
    sys.path.insert(0, str(ROOT))
    from ontology.phenomenal_extra_entity_detector import PhenomenalExtraEntityDetector

    r = PhenomenalExtraEntityDetector().step(inputs=ready_aq3_inputs(), persist=False)
    assert r["phenomenal_extra_entity_status"] == "PHENOMENAL_EXTRA_ENTITIES_DETECTED"
    assert r["extra_entity_detection_completed"] is True
    assert r["step"] == "AQ3"
    assert r["axis"] == "AQ"
    assert r["public_schema_version"] == "AQ3.phenomenal_extra_entity_detector.v1"
    assert r["ap_dependency_status"] == "AP_RESOLVED"
    assert r["aq1_dependency_status"] == "AQ1_RESOLVED"
    assert r["aq2_dependency_status"] == "AQ2_RESOLVED"
    assert len(r["phenomenal_extra_entities"]) >= 7
    for item in r["phenomenal_extra_entities"]:
        assert 0.0 <= item["extra_entity_burden_score"] <= 1.0
        assert item["burden_classification"] in {
            "minimal_extra_entity_burden",
            "moderate_extra_entity_burden",
            "high_extra_entity_burden",
            "severe_extra_entity_burden",
        }
        assert item["phenomenal_entity_proven"] is False
        assert item["consciousness_proven"] is False
        assert item["phenomenology_undetermined"] is True
    assert_numeric_bounds(r["extra_entity_metrics"])
    assert r["extra_entity_metrics"]["ontological_proof_score"] == 0.0
    assert r["extra_entity_metrics"]["phenomenal_proof_score"] == 0.0
    assert r["extra_entity_metrics"]["phenomenal_entity_proof_score"] == 0.0
    assert_epistemic_guards(r)
    assert r["next_recommended_module"] == "no_difference_penalty_checker"

    a = PhenomenalExtraEntityDetector().step(inputs=ready_aq3_inputs(), persist=False)
    b = PhenomenalExtraEntityDetector().step(inputs=ready_aq3_inputs(), persist=False)
    assert a["phenomenal_extra_entities"] == b["phenomenal_extra_entities"]
    assert a["extra_entity_metrics"] == b["extra_entity_metrics"]

    degraded_inputs = ready_aq3_inputs()
    degraded_inputs["aq2"] = {
        **EPISTEMIC_STATUS,
        "cost_analysis_completed": False,
        "rival_theory_costs": [],
        "cost_metrics": {},
    }
    degraded = PhenomenalExtraEntityDetector().step(inputs=degraded_inputs, persist=False)
    assert degraded["phenomenal_extra_entity_status"] == "PHENOMENAL_EXTRA_ENTITY_DETECTION_INCOMPLETE"
    assert degraded["extra_entity_detection_completed"] is False
    assert degraded["consciousness_proven"] is False
    assert degraded["phenomenology_undetermined"] is True

    persisted = PhenomenalExtraEntityDetector().step(inputs=ready_aq3_inputs(), persist=True)
    assert_persistence(persisted)
    assert_inventory_and_registry()
    print("AQ3_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
