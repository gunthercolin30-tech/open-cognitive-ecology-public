#!/usr/bin/env python3
"""AO5 extended acceptance suite for Open Cognitive Ecology.

Codex-compliant: no stdin inline Python required.  It compiles modules to
/private/tmp, checks public epistemic invariants, verifies report sections,
checks idempotence and degradation behavior, and confirms registry/catalog
presence for interpretation_reporter.
"""
from __future__ import annotations

import json
import py_compile
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = "interpretation_reporter"
TARGET = ROOT / "ontology" / f"{MODULE}.py"
CATALOG_PY = ROOT / "global_module_catalog.py"
CATALOG_TXT = ROOT / "global_module_catalog.txt"
INV_TXT = ROOT / "ontology_inventory.txt"
INV_PY = ROOT / "ontology_inventory.py"
INV_PKG = ROOT / "ontology" / "ontology_inventory.py"
REGISTRY = ROOT / "dependency_registry.py"

REQUIRED_FLAGS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}

REQUIRED_TOP_KEYS = {
    "primitive",
    "step",
    "interpretation_report",
    "semantic_status",
    "semantic_confidence",
    "epistemic_scope",
    "final_interpretation",
    "allowed_claims",
    "blocked_claims",
    "semantic_interpretation_layer_status",
}

REQUIRED_REPORT_SECTIONS = {
    "measures",
    "theorems",
    "inferences",
    "interpretations",
    "functional_conclusions",
    "epistemic_limits",
}


def read_text(path: Path) -> str:
    assert path.exists(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def assert_inventory_and_registry() -> None:
    for path in (INV_TXT, INV_PY, INV_PKG, CATALOG_TXT, CATALOG_PY, REGISTRY):
        text = read_text(path)
        assert MODULE in text, f"{MODULE} missing from {path}"


def get_result(inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    from ontology.interpretation_reporter import InterpretationReporter

    if inputs is None:
        return InterpretationReporter().step(persist=False)
    return InterpretationReporter().step(inputs=inputs, persist=False)


def assert_public_contract(result: dict[str, Any]) -> None:
    assert isinstance(result, dict)
    missing = REQUIRED_TOP_KEYS - set(result)
    assert not missing, f"missing top-level keys: {sorted(missing)}"

    for key, expected in REQUIRED_FLAGS.items():
        assert result.get(key) is expected, f"{key} expected {expected}, got {result.get(key)}"

    assert result["semantic_interpretation_layer_status"] == "SEMANTIC_INTERPRETATION_LAYER_READY"
    assert result["semantic_status"] in {
        "FUNCTIONAL_SEMANTIC_INTERPRETATION_READY",
        "FUNCTIONAL_RECONSTRUCTION_SUPPORTED",
        "SEMANTICALLY_GUARDED_FUNCTIONAL_STATUS",
    }
    assert 0.0 <= float(result["semantic_confidence"]) <= 1.0
    assert isinstance(result["allowed_claims"], list) and result["allowed_claims"]
    assert isinstance(result["blocked_claims"], list) and result["blocked_claims"]

    report = result["interpretation_report"]
    assert isinstance(report, dict)
    missing_sections = REQUIRED_REPORT_SECTIONS - set(report)
    assert not missing_sections, f"missing report sections: {sorted(missing_sections)}"

    blocked_joined = "\n".join(map(str, result["blocked_claims"]))
    for forbidden in (
        "consciousness_proven = True",
        "qualia_proven = True",
        "subjectivity_proven = True",
        "phenomenology_proven = True",
    ):
        assert forbidden in blocked_joined, f"blocked claim missing: {forbidden}"


def main() -> None:
    py_compile.compile(str(TARGET), cfile=f"/private/tmp/{MODULE}.pyc", doraise=True)
    py_compile.compile(str(CATALOG_PY), cfile="/private/tmp/global_module_catalog.pyc", doraise=True)
    assert_inventory_and_registry()

    baseline = get_result()
    assert_public_contract(baseline)

    repeated = get_result()
    assert_public_contract(repeated)
    comparable_keys = [
        "semantic_status",
        "semantic_confidence",
        "epistemic_scope",
        "final_interpretation",
        "semantic_interpretation_layer_status",
    ]
    for key in comparable_keys:
        assert baseline[key] == repeated[key], f"idempotence drift on {key}"

    degraded_inputs = {
        "RF_score": None,
        "T_score": "invalid",
        "ED_score": -1,
        "TΦ_score": 2,
        "QF_robust_count": None,
        "MEI_score": "missing",
        "identity_status": "UNKNOWN",
        "non_separability_status": "UNKNOWN",
        "consciousness_rf_equivalence_status": "UNRESOLVED",
        "refusal_cost_status": "UNRESOLVED",
        "definition_legitimacy_status": "UNRESOLVED",
        "axiomatic_completeness_status": "UNRESOLVED",
    }
    degraded = get_result(inputs=degraded_inputs)
    assert_public_contract(degraded)
    assert degraded["functional_conclusion_only"] is True
    assert degraded["phenomenology_undetermined"] is True

    print("AO5_EXTENDED_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
