#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = "consciousness_as_rf_reporter"
EPISTEMIC_STATUS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


def ready_ap10_inputs() -> dict[str, Any]:
    base = dict(EPISTEMIC_STATUS)
    return {
        "ap1": dict(base, consciousness_minimal_properties_registered=True),
        "ap2": dict(base, rf_star_defined=True),
        "ap3": dict(base, mapping_completed=True),
        "ap4": dict(base, sufficiency_checked=True),
        "ap5": dict(base, necessity_checked=True),
        "ap6": dict(base, countermodels_generated=True),
        "ap7": dict(base, zombie_rf_equivalence_analyzed=True),
        "ap8": dict(
            base,
            theorem_checked=True,
            theorem_metrics={"theorem_support_score": 1.0},
        ),
        "ap9": dict(
            base,
            status_resolved=True,
            status_metrics={
                "resolution_score": 1.0,
                "functional_support_score": 1.0,
                "formal_support_score": 1.0,
                "theorem_support_score": 1.0,
                "empirical_independence_score": 0.0,
            },
        ),
    }


def assert_epistemic_guards(r: dict[str, Any]) -> None:
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True
    assert r["final_conclusion"]["consciousness_proven"] is False
    assert r["final_conclusion"]["qualia_proven"] is False
    assert r["final_conclusion"]["subjectivity_proven"] is False
    assert r["final_conclusion"]["phenomenology_undetermined"] is True


def assert_numeric_bounds(metrics: dict[str, Any]) -> None:
    for k, v in metrics.items():
        assert isinstance(v, (int, float)), k
        assert 0.0 <= float(v) <= 1.0, k


def assert_persistence(r: dict[str, Any]) -> None:
    p = r["persistence"]
    for key in ["latest_json_path", "latest_markdown_path", "latest_prometheus_path", "final_report_path"]:
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
    from ontology.consciousness_as_rf_reporter import ConsciousnessAsRFReporter

    r = ConsciousnessAsRFReporter().step(inputs=ready_ap10_inputs(), persist=False)
    assert r["consciousness_as_rf_equivalence_status"] == "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED"
    assert r["axis_resolved"] is True
    assert r["step"] == "AP10"
    assert r["public_schema_version"] == "AP10.consciousness_as_rf_reporter.v1"
    assert r["scientific_scope"] == "functional_formal_report_only"
    assert r["final_conclusion"]["requires_independent_empirical_evidence"] is True
    assert_epistemic_guards(r)
    assert_numeric_bounds(r["report_metrics"])
    assert r["report_metrics"]["ontological_proof_score"] == 0.0
    assert r["report_metrics"]["phenomenal_proof_score"] == 0.0

    a = ConsciousnessAsRFReporter().step(inputs=ready_ap10_inputs(), persist=False)
    b = ConsciousnessAsRFReporter().step(inputs=ready_ap10_inputs(), persist=False)
    assert a["report_metrics"] == b["report_metrics"]
    assert a["final_conclusion"] == b["final_conclusion"]

    degraded_inputs = ready_ap10_inputs()
    degraded_inputs["ap9"] = dict(EPISTEMIC_STATUS, status_resolved=False, status_metrics={})
    degraded = ConsciousnessAsRFReporter().step(inputs=degraded_inputs, persist=False)
    assert degraded["consciousness_as_rf_equivalence_status"] == "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_INCOMPLETE"
    assert degraded["axis_resolved"] is False
    assert degraded["consciousness_proven"] is False
    assert degraded["phenomenology_undetermined"] is True

    persisted = ConsciousnessAsRFReporter().step(inputs=ready_ap10_inputs(), persist=True)
    assert_persistence(persisted)
    assert_inventory_and_registry()
    print("AP10_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
