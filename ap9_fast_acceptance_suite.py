#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
EPISTEMIC_STATUS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


def ready_ap9_inputs() -> dict[str, Any]:
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
    }


def assert_epistemic_guards(r: dict[str, Any]) -> None:
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_undetermined"] is True
    assert r["functional_conclusion_only"] is True


def assert_numeric_bounds(metrics: dict[str, Any]) -> None:
    for k, v in metrics.items():
        assert isinstance(v, (int, float)), k
        assert 0.0 <= float(v) <= 1.0, k


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


def main() -> None:
    import sys
    sys.path.insert(0, str(ROOT))
    from ontology.consciousness_proven_status_resolver import ConsciousnessProvenStatusResolver

    r = ConsciousnessProvenStatusResolver().step(inputs=ready_ap9_inputs(), persist=False)
    assert r["consciousness_proven_status"] == "CONSCIOUSNESS_PROVEN_STATUS_RESOLVED"
    assert r["status_resolved"] is True
    assert r["public_schema_version"] == "AP9.consciousness_proven_status_resolver.v1"
    assert r["status_taxonomy"]["ontological_properties"] == "ONTOLOGICAL_CONSCIOUSNESS_NOT_PROVEN"
    assert r["status_taxonomy"]["phenomenological_properties"] == "PHENOMENOLOGY_UNDETERMINED"
    assert_epistemic_guards(r)
    assert_numeric_bounds(r["status_metrics"])
    assert r["status_metrics"]["ontological_proof_score"] == 0.0
    assert r["status_metrics"]["phenomenal_proof_score"] == 0.0

    a = ConsciousnessProvenStatusResolver().step(inputs=ready_ap9_inputs(), persist=False)
    b = ConsciousnessProvenStatusResolver().step(inputs=ready_ap9_inputs(), persist=False)
    assert a["status_metrics"] == b["status_metrics"]
    assert a["status_taxonomy"] == b["status_taxonomy"]

    degraded_inputs = ready_ap9_inputs()
    degraded_inputs["ap8"] = dict(EPISTEMIC_STATUS, theorem_checked=False, theorem_metrics={})
    degraded = ConsciousnessProvenStatusResolver().step(inputs=degraded_inputs, persist=False)
    assert degraded["consciousness_proven_status"] == "CONSCIOUSNESS_PROVEN_STATUS_INCOMPLETE"
    assert degraded["status_resolved"] is False
    assert degraded["consciousness_proven"] is False
    assert degraded["phenomenology_undetermined"] is True

    persisted = ConsciousnessProvenStatusResolver().step(inputs=ready_ap9_inputs(), persist=True)
    assert_persistence(persisted)
    assert_inventory_and_registry("consciousness_proven_status_resolver")
    print("AP9_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
