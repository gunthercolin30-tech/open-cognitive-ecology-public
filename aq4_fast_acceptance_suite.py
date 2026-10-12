#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = "no_difference_penalty_checker"
EPISTEMIC_STATUS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


def ready_aq4_inputs() -> dict[str, Any]:
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
    phenomenal_extra_entities = [
        {
            "rival_theory": "Dualism",
            "extra_entity_burden_score": 0.94,
            "parsimony_violation_score": 0.92,
        },
        {
            "rival_theory": "IIT",
            "extra_entity_burden_score": 0.44,
            "parsimony_violation_score": 0.38,
        },
        {
            "rival_theory": "GWT",
            "extra_entity_burden_score": 0.48,
            "parsimony_violation_score": 0.42,
        },
        {
            "rival_theory": "HOT",
            "extra_entity_burden_score": 0.50,
            "parsimony_violation_score": 0.44,
        },
        {
            "rival_theory": "Predictive Processing",
            "extra_entity_burden_score": 0.40,
            "parsimony_violation_score": 0.34,
        },
        {
            "rival_theory": "Classical Functionalism",
            "extra_entity_burden_score": 0.68,
            "parsimony_violation_score": 0.70,
        },
        {
            "rival_theory": "Eliminativism",
            "extra_entity_burden_score": 0.88,
            "parsimony_violation_score": 0.86,
        },
    ]
    return {
        "aq1": dict(
            base,
            taxonomy_initialized=True,
            consciousness_refusal_taxonomy_status="CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED",
            refusal_taxonomy=[{"name": "no_difference_refusal"}],
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
        "aq3": dict(
            base,
            extra_entity_detection_completed=True,
            phenomenal_extra_entity_status="PHENOMENAL_EXTRA_ENTITIES_DETECTED",
            phenomenal_extra_entities=phenomenal_extra_entities,
            extra_entity_metrics={
                "ontological_proof_score": 0.0,
                "phenomenal_proof_score": 0.0,
                "phenomenal_entity_proof_score": 0.0,
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
    assert "phenomenal_extra_entity_detector" in dependency_registry.DEPENDENCY_REGISTRY[MODULE]
    py_compile.compile(
        str(ROOT / "ontology" / f"{MODULE}.py"),
        cfile=str(Path("/private/tmp") / f"oce_{MODULE}.pyc"),
        doraise=True,
    )


def main() -> None:
    import sys
    sys.path.insert(0, str(ROOT))
    from ontology.no_difference_penalty_checker import NoDifferencePenaltyChecker

    r = NoDifferencePenaltyChecker().step(inputs=ready_aq4_inputs(), persist=False)
    assert r["no_difference_penalty_status"] == "NO_DIFFERENCE_PENALTY_CHECKED"
    assert r["penalty_check_completed"] is True
    assert r["step"] == "AQ4"
    assert r["axis"] == "AQ"
    assert r["public_schema_version"] == "AQ4.no_difference_penalty_checker.v1"
    assert r["ap_dependency_status"] == "AP_RESOLVED"
    assert r["aq1_dependency_status"] == "AQ1_RESOLVED"
    assert r["aq2_dependency_status"] == "AQ2_RESOLVED"
    assert r["aq3_dependency_status"] == "AQ3_RESOLVED"
    assert len(r["no_difference_penalties"]) >= 7
    for item in r["no_difference_penalties"]:
        assert 0.0 <= item["no_difference_penalty_score"] <= 1.0
        assert item["penalty_classification"] in {
            "low_no_difference_penalty",
            "moderate_no_difference_penalty",
            "high_no_difference_penalty",
            "severe_no_difference_penalty",
        }
        assert item["consciousness_proven"] is False
        assert item["phenomenology_undetermined"] is True
    assert_numeric_bounds(r["penalty_metrics"])
    assert r["penalty_metrics"]["ontological_proof_score"] == 0.0
    assert r["penalty_metrics"]["phenomenal_proof_score"] == 0.0
    assert r["penalty_metrics"]["consciousness_proof_score"] == 0.0
    assert_epistemic_guards(r)
    assert r["next_recommended_module"] == "minimal_property_denial_checker"

    a = NoDifferencePenaltyChecker().step(inputs=ready_aq4_inputs(), persist=False)
    b = NoDifferencePenaltyChecker().step(inputs=ready_aq4_inputs(), persist=False)
    assert a["no_difference_penalties"] == b["no_difference_penalties"]
    assert a["penalty_metrics"] == b["penalty_metrics"]

    degraded_inputs = ready_aq4_inputs()
    degraded_inputs["aq3"] = {
        **EPISTEMIC_STATUS,
        "extra_entity_detection_completed": False,
        "phenomenal_extra_entities": [],
        "extra_entity_metrics": {},
    }
    degraded = NoDifferencePenaltyChecker().step(inputs=degraded_inputs, persist=False)
    assert degraded["no_difference_penalty_status"] == "NO_DIFFERENCE_PENALTY_CHECK_INCOMPLETE"
    assert degraded["penalty_check_completed"] is False
    assert degraded["consciousness_proven"] is False
    assert degraded["phenomenology_undetermined"] is True

    persisted = NoDifferencePenaltyChecker().step(inputs=ready_aq4_inputs(), persist=True)
    assert_persistence(persisted)
    assert_inventory_and_registry()
    print("AQ4_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
