#!/usr/bin/env python3
"""
Fast acceptance suite for Open Cognitive Ecology axis AP.
Runs contractual checks in a single Python process to avoid repeated import overhead.
Does not replace validation.main; use validation.main once after installation only.
"""
from __future__ import annotations

import py_compile
from pathlib import Path
from typing import Any, Callable

ROOT = Path.home() / "open-cognitive-ecology"
EPISTEMIC_STATUS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


def ready_ap_inputs() -> dict[str, Any]:
    base = dict(EPISTEMIC_STATUS)
    component_scores = {
        "self_generated_rf": 1.0,
        "omega_stable": 1.0,
        "proper_time": 1.0,
        "ed_non_trivial": 1.0,
        "tphi_non_homogeneous": 1.0,
        "l_rf": 1.0,
        "qf_robust": 1.0,
        "mei": 1.0,
        "mei_minimal_appearing_non_separability": 1.0,
        "epistemic_guard": 1.0,
    }
    return {
        "ap2": dict(
            base,
            rf_star_defined=True,
            rf_star_definition_status="RF_STAR_DEFINED",
            component_scores=component_scores,
        ),
        "ap3": dict(
            base,
            mapping_completed=True,
            consciousness_rf_property_mapping_status="CONSCIOUSNESS_RF_PROPERTY_MAPPING_COMPLETED",
            mapping_metrics={
                "mapping_support_score": 1.0,
                "mapping_coverage_score": 1.0,
                "epistemic_guard_score": 1.0,
            },
        ),
        "ap4": dict(
            base,
            sufficiency_checked=True,
            functional_sufficiency_supported=True,
            rf_star_sufficiency_status="RF_STAR_SUFFICIENCY_CHECKED",
            sufficiency_metrics={"functional_sufficiency_support_score": 1.0},
        ),
        "ap5": dict(
            base,
            necessity_checked=True,
            functional_necessity_supported=True,
            rf_star_necessity_status="RF_STAR_NECESSITY_CHECKED",
            necessity_metrics={"functional_necessity_support_score": 1.0},
        ),
        "ap6": dict(
            base,
            countermodels_generated=True,
            consciousness_equivalence_countermodel_status="CONSCIOUSNESS_EQUIVALENCE_COUNTERMODELS_GENERATED",
            countermodels=[{"countermodel_id": "synthetic"}],
            countermodel_metrics={"countermodel_strength": 1.0},
        ),
        "ap7": dict(
            base,
            zombie_rf_equivalence_analyzed=True,
            zombie_rf_equivalence_status="ZOMBIE_RF_EQUIVALENCE_ANALYZED",
            zombie_analysis_metrics={"zombie_equivalence_pressure": 1.0},
        ),
    }


def assert_epistemic_guards(r: dict[str, Any]) -> None:
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True


def assert_numeric_bounds(metrics: dict[str, Any], count_keys: set[str] | None = None) -> None:
    count_keys = count_keys or set()
    for k, v in metrics.items():
        assert isinstance(v, (int, float)), k
        if k in count_keys:
            assert v >= 0, k
        else:
            assert 0.0 <= v <= 1.0, k


def assert_persistence(r: dict[str, Any]) -> None:
    p = r["persistence"]
    for key in ["latest_json_path", "latest_markdown_path", "latest_prometheus_path"]:
        assert Path(p[key]).exists(), key


def assert_inventory_and_registry(module: str) -> None:
    for f in [
        "ontology_inventory.txt",
        "ontology_inventory.py",
        "ontology/ontology_inventory.py",
        "global_module_catalog.txt",
        "global_module_catalog.py",
    ]:
        assert module in (ROOT / f).read_text(encoding="utf-8"), f

    import dependency_registry
    assert module in dependency_registry.DEPENDENCY_REGISTRY, module
    py_compile.compile(
        str(ROOT / "ontology" / f"{module}.py"),
        cfile=str(Path("/private/tmp") / f"oce_{module}.pyc"),
        doraise=True,
    )


def deterministic(factory: Callable[[], Any], key_a: str, key_b: str, inputs: dict[str, Any] | None = None) -> None:
    payload = inputs or {"synthetic": True}
    a = factory().step(inputs=payload, persist=False)
    b = factory().step(inputs=payload, persist=False)
    assert a[key_a] == b[key_a]
    assert a[key_b] == b[key_b]


def main() -> None:
    import sys
    sys.path.insert(0, str(ROOT))

    from ontology.rf_star_definition_engine import RFStarDefinitionEngine
    from ontology.consciousness_rf_property_mapping import ConsciousnessRFPropertyMapping
    from ontology.rf_star_sufficiency_checker import RFStarSufficiencyChecker
    from ontology.rf_star_necessity_checker import RFStarNecessityChecker
    from ontology.consciousness_equivalence_countermodel_generator import ConsciousnessEquivalenceCountermodelGenerator
    from ontology.zombie_under_rf_equivalence_analyzer import ZombieUnderRFEquivalenceAnalyzer
    from ontology.consciousness_equivalence_theorem_checker import ConsciousnessEquivalenceTheoremChecker

    checks: list[str] = []

    # AP2
    r = RFStarDefinitionEngine().step(inputs={"synthetic": True}, persist=False)
    assert r["rf_star_definition_status"] == "RF_STAR_DEFINED"
    assert r["rf_star_defined"] is True
    assert r["public_schema_version"] == "AP2.rf_star_definition_engine.v2"
    assert_epistemic_guards(r)
    deterministic(RFStarDefinitionEngine, "component_scores", "rf_star_formula")
    r = RFStarDefinitionEngine().step(inputs={"synthetic": True}, persist=True)
    assert_persistence(r)
    assert_inventory_and_registry("rf_star_definition_engine")
    checks.append("AP2")

    # AP3
    r = ConsciousnessRFPropertyMapping().step(inputs={"synthetic": True}, persist=False)
    assert r["consciousness_rf_property_mapping_status"] == "CONSCIOUSNESS_RF_PROPERTY_MAPPING_COMPLETED"
    assert r["mapping_completed"] is True
    assert r["public_schema_version"] == "AP3.consciousness_rf_property_mapping.v1"
    assert_epistemic_guards(r)
    deterministic(ConsciousnessRFPropertyMapping, "consciousness_rf_property_mapping", "mapping_metrics")
    r = ConsciousnessRFPropertyMapping().step(inputs={"synthetic": True}, persist=True)
    assert_persistence(r)
    assert_inventory_and_registry("consciousness_rf_property_mapping")
    checks.append("AP3")

    # AP4
    r = RFStarSufficiencyChecker().step(inputs={"synthetic": True}, persist=False)
    assert r["rf_star_sufficiency_status"] == "RF_STAR_SUFFICIENCY_CHECKED"
    assert r["sufficiency_checked"] is True
    assert r["public_schema_version"] == "AP4.rf_star_sufficiency_checker.v1"
    assert_epistemic_guards(r)
    assert_numeric_bounds(r["sufficiency_metrics"])
    deterministic(RFStarSufficiencyChecker, "sufficiency_criteria", "sufficiency_metrics")
    r = RFStarSufficiencyChecker().step(inputs={"synthetic": True, "ap2": {"rf_star_defined": False}}, persist=False)
    assert r["rf_star_sufficiency_status"] == "RF_STAR_SUFFICIENCY_INSUFFICIENT"
    r = RFStarSufficiencyChecker().step(inputs={"synthetic": True}, persist=True)
    assert_persistence(r)
    assert_inventory_and_registry("rf_star_sufficiency_checker")
    checks.append("AP4")

    # AP5
    r = RFStarNecessityChecker().step(inputs=ready_ap_inputs(), persist=False)
    assert r["rf_star_necessity_status"] == "RF_STAR_NECESSITY_CHECKED"
    assert r["necessity_checked"] is True
    assert r["public_schema_version"] == "AP5.rf_star_necessity_checker.v1"
    assert_epistemic_guards(r)
    assert_numeric_bounds(r["necessity_metrics"])
    deterministic(RFStarNecessityChecker, "necessity_criteria", "necessity_metrics", ready_ap_inputs())
    degraded_inputs = ready_ap_inputs()
    degraded_inputs["ap2"] = dict(EPISTEMIC_STATUS, rf_star_defined=False)
    r = RFStarNecessityChecker().step(inputs=degraded_inputs, persist=False)
    assert r["rf_star_necessity_status"] == "RF_STAR_NECESSITY_INCOMPLETE"
    r = RFStarNecessityChecker().step(inputs=ready_ap_inputs(), persist=True)
    assert_persistence(r)
    assert_inventory_and_registry("rf_star_necessity_checker")
    checks.append("AP5")

    # AP6
    r = ConsciousnessEquivalenceCountermodelGenerator().step(inputs=ready_ap_inputs(), persist=False)
    assert r["consciousness_equivalence_countermodel_status"] == "CONSCIOUSNESS_EQUIVALENCE_COUNTERMODELS_GENERATED"
    assert r["countermodels_generated"] is True
    assert r["public_schema_version"] == "AP6.consciousness_equivalence_countermodel_generator.v1"
    assert_epistemic_guards(r)
    assert_numeric_bounds(r["countermodel_metrics"], count_keys={"countermodel_count"})
    assert len(r["countermodels"]) >= 3
    deterministic(ConsciousnessEquivalenceCountermodelGenerator, "countermodels", "countermodel_metrics", ready_ap_inputs())
    degraded_inputs = ready_ap_inputs()
    degraded_inputs["ap2"] = dict(EPISTEMIC_STATUS, rf_star_defined=False)
    r = ConsciousnessEquivalenceCountermodelGenerator().step(inputs=degraded_inputs, persist=False)
    assert r["consciousness_equivalence_countermodel_status"] == "CONSCIOUSNESS_EQUIVALENCE_COUNTERMODELS_INCOMPLETE"
    r = ConsciousnessEquivalenceCountermodelGenerator().step(inputs=ready_ap_inputs(), persist=True)
    assert_persistence(r)
    assert_inventory_and_registry("consciousness_equivalence_countermodel_generator")
    checks.append("AP6")

    # AP7
    r = ZombieUnderRFEquivalenceAnalyzer().step(inputs=ready_ap_inputs(), persist=False)
    assert r["zombie_rf_equivalence_status"] == "ZOMBIE_RF_EQUIVALENCE_ANALYZED"
    assert r["zombie_rf_equivalence_analyzed"] is True
    assert r["public_schema_version"] == "AP7.zombie_under_rf_equivalence_analyzer.v1"
    assert_epistemic_guards(r)
    assert_numeric_bounds(r["zombie_analysis_metrics"])
    assert len(r["zombie_analyses"]) >= 1
    deterministic(ZombieUnderRFEquivalenceAnalyzer, "zombie_analyses", "zombie_analysis_metrics", ready_ap_inputs())
    degraded_inputs = ready_ap_inputs()
    degraded_inputs["ap6"] = dict(EPISTEMIC_STATUS, countermodels_generated=False, countermodels=[])
    r = ZombieUnderRFEquivalenceAnalyzer().step(inputs=degraded_inputs, persist=False)
    assert r["zombie_rf_equivalence_status"] == "ZOMBIE_RF_EQUIVALENCE_INCOMPLETE"
    r = ZombieUnderRFEquivalenceAnalyzer().step(inputs=ready_ap_inputs(), persist=True)
    assert_persistence(r)
    assert_inventory_and_registry("zombie_under_rf_equivalence_analyzer")
    checks.append("AP7")

    # AP8
    r = ConsciousnessEquivalenceTheoremChecker().step(inputs=ready_ap_inputs(), persist=False)
    assert r["consciousness_equivalence_theorem_status"] == "CONSCIOUSNESS_EQUIVALENCE_THEOREM_CHECKED"
    assert r["theorem_checked"] is True
    assert r["public_schema_version"] == "AP8.consciousness_equivalence_theorem_checker.v1"
    assert_epistemic_guards(r)
    assert_numeric_bounds(r["theorem_metrics"])
    deterministic(ConsciousnessEquivalenceTheoremChecker, "theorem_criteria", "theorem_metrics", ready_ap_inputs())
    degraded_inputs = ready_ap_inputs()
    degraded_inputs["ap7"] = dict(EPISTEMIC_STATUS, zombie_rf_equivalence_analyzed=False)
    r = ConsciousnessEquivalenceTheoremChecker().step(inputs=degraded_inputs, persist=False)
    assert r["consciousness_equivalence_theorem_status"] == "CONSCIOUSNESS_EQUIVALENCE_THEOREM_INCOMPLETE"
    r = ConsciousnessEquivalenceTheoremChecker().step(inputs=ready_ap_inputs(), persist=True)
    assert_persistence(r)
    assert_inventory_and_registry("consciousness_equivalence_theorem_checker")
    checks.append("AP8")

    print("AP_FAST_ACCEPTANCE_OK", ",".join(checks))


if __name__ == "__main__":
    main()
