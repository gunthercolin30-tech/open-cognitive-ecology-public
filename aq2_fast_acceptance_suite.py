#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = "rival_theory_cost_analyzer"
EPISTEMIC_STATUS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


def ready_aq2_inputs() -> dict[str, Any]:
    base = dict(EPISTEMIC_STATUS)
    refusal_taxonomy = [
        {
            "name": "rival_theory_preference_refusal",
            "scientific_admissibility": "comparative",
            "expected_cost_type": "rival_theory_explanatory_cost",
        }
    ]
    return {
        "aq1": dict(
            base,
            taxonomy_initialized=True,
            consciousness_refusal_taxonomy_status="CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED",
            refusal_taxonomy=refusal_taxonomy,
            taxonomy_metrics={
                "ap_equivalence_dependency_score": 1.0,
                "functional_equivalence_support_score": 1.0,
                "formal_equivalence_support_score": 1.0,
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
    assert "consciousness_refusal_taxonomy" in dependency_registry.DEPENDENCY_REGISTRY[MODULE]
    py_compile.compile(
        str(ROOT / "ontology" / f"{MODULE}.py"),
        cfile=str(Path("/private/tmp") / f"oce_{MODULE}.pyc"),
        doraise=True,
    )


def main() -> None:
    import sys
    sys.path.insert(0, str(ROOT))
    from ontology.rival_theory_cost_analyzer import RivalTheoryCostAnalyzer

    r = RivalTheoryCostAnalyzer().step(inputs=ready_aq2_inputs(), persist=False)
    assert r["rival_theory_cost_status"] == "RIVAL_THEORY_COST_ANALYZED"
    assert r["cost_analysis_completed"] is True
    assert r["step"] == "AQ2"
    assert r["axis"] == "AQ"
    assert r["public_schema_version"] == "AQ2.rival_theory_cost_analyzer.v1"
    assert r["ap_dependency_status"] == "AP_RESOLVED"
    assert r["aq1_dependency_status"] == "AQ1_RESOLVED"
    assert len(r["rival_theory_costs"]) >= 7
    assert {x["name"] for x in r["rival_theory_costs"]} >= {
        "IIT",
        "GWT",
        "HOT",
        "Predictive Processing",
        "Classical Functionalism",
        "Dualism",
        "Eliminativism",
    }
    for item in r["rival_theory_costs"]:
        assert 0.0 <= item["refusal_cost_score"] <= 1.0
        assert item["cost_level"] in {"low", "moderate", "high", "very_high"}
        assert item["consciousness_proven"] is False
        assert item["phenomenology_undetermined"] is True
    assert_numeric_bounds(r["cost_metrics"])
    assert r["cost_metrics"]["ontological_proof_score"] == 0.0
    assert r["cost_metrics"]["phenomenal_proof_score"] == 0.0
    assert_epistemic_guards(r)
    assert r["next_recommended_module"] == "phenomenal_extra_entity_detector"

    a = RivalTheoryCostAnalyzer().step(inputs=ready_aq2_inputs(), persist=False)
    b = RivalTheoryCostAnalyzer().step(inputs=ready_aq2_inputs(), persist=False)
    assert a["rival_theory_costs"] == b["rival_theory_costs"]
    assert a["cost_metrics"] == b["cost_metrics"]

    degraded_inputs = ready_aq2_inputs()
    degraded_inputs["aq1"] = {
        **EPISTEMIC_STATUS,
        "taxonomy_initialized": False,
        "refusal_taxonomy": [],
        "taxonomy_metrics": {},
    }
    degraded = RivalTheoryCostAnalyzer().step(inputs=degraded_inputs, persist=False)
    assert degraded["rival_theory_cost_status"] == "RIVAL_THEORY_COST_ANALYSIS_INCOMPLETE"
    assert degraded["cost_analysis_completed"] is False
    assert degraded["consciousness_proven"] is False
    assert degraded["phenomenology_undetermined"] is True

    persisted = RivalTheoryCostAnalyzer().step(inputs=ready_aq2_inputs(), persist=True)
    assert_persistence(persisted)
    assert_inventory_and_registry()
    print("AQ2_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
