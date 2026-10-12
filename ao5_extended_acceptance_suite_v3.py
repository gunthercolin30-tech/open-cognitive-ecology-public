#!/usr/bin/env python3
"""
AO5 extended acceptance suite v3.
No inline Python required by the user; execute as a file.
Checks only stable public invariants for ontology.interpretation_reporter.
"""
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = ROOT / "ontology" / "interpretation_reporter.py"
CATALOG_PY = ROOT / "global_module_catalog.py"


def assert_file_contains(path: Path, needle: str) -> None:
    assert path.exists(), f"missing file: {path}"
    text = path.read_text(encoding="utf-8")
    assert needle in text, f"missing {needle!r} in {path.name}"


def assert_public_contract(result: dict) -> None:
    required_keys = {
        "primitive",
        "interpretation_report",
        "semantic_status",
        "semantic_confidence",
        "epistemic_scope",
        "final_interpretation",
        "allowed_claims",
        "blocked_claims",
        "semantic_interpretation_layer_status",
        "consciousness_proven",
        "qualia_proven",
        "subjectivity_proven",
        "phenomenology_proven",
        "phenomenology_undetermined",
        "functional_conclusion_only",
    }
    missing = required_keys - set(result)
    assert not missing, f"missing keys: {sorted(missing)}"

    assert result["primitive"] == "INTERPRETATION_REPORTER"
    assert result["semantic_interpretation_layer_status"] == "SEMANTIC_INTERPRETATION_LAYER_READY"
    assert isinstance(result["interpretation_report"], dict)
    assert isinstance(result["semantic_status"], str)
    assert isinstance(result["semantic_confidence"], (int, float))
    assert 0.0 <= float(result["semantic_confidence"]) <= 1.0
    assert isinstance(result["epistemic_scope"], str)
    assert isinstance(result["final_interpretation"], str)
    assert isinstance(result["allowed_claims"], list)
    assert isinstance(result["blocked_claims"], list)

    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True

    blocked = " ".join(str(x) for x in result["blocked_claims"]).lower()
    assert "consciousness" in blocked
    assert "qualia" in blocked
    assert "phenomenology" in blocked or "phenomenal" in blocked

    report = result["interpretation_report"]
    for section in [
        "measurements",
        "theorems",
        "inferences",
        "interpretations",
        "functional_conclusions",
        "epistemic_limits",
    ]:
        assert section in report, f"missing report section: {section}"


def main() -> None:
    assert MODULE.exists(), MODULE
    py_compile.compile(str(MODULE), cfile="/private/tmp/interpretation_reporter.pyc", doraise=True)
    py_compile.compile(str(CATALOG_PY), cfile="/private/tmp/global_module_catalog.pyc", doraise=True)

    assert_file_contains(ROOT / "ontology_inventory.txt", "interpretation_reporter")
    assert_file_contains(ROOT / "ontology_inventory.py", "interpretation_reporter")
    assert_file_contains(ROOT / "ontology" / "ontology_inventory.py", "interpretation_reporter")
    assert_file_contains(ROOT / "global_module_catalog.txt", "interpretation_reporter")
    assert_file_contains(ROOT / "global_module_catalog.py", "interpretation_reporter")
    assert_file_contains(ROOT / "dependency_registry.py", "interpretation_reporter")

    from ontology.interpretation_reporter import InterpretationReporter

    ready_context = {
        "RF_score": 0.93,
        "T_score": 0.91,
        "ED_score": 0.88,
        "TΦ_score": 0.87,
        "QF_robust_count": 8,
        "MEI_score": 0.90,
        "identity_status": "IDENTITY_STABLE",
        "non_separability_status": "NON_SEPARABILITY_SUPPORTED",
        "consciousness_rf_equivalence_status": "RF_EQUIVALENCE_SUPPORTED",
        "refusal_cost_status": "REFUSAL_COST_MEASURABLE",
        "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
        "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
    }

    baseline = InterpretationReporter().step(inputs=ready_context, persist=False)
    repeated = InterpretationReporter().step(inputs=ready_context, persist=False)
    degraded = InterpretationReporter().step(inputs={}, persist=False)

    assert_public_contract(baseline)
    assert_public_contract(repeated)
    assert_public_contract(degraded)
    assert baseline == repeated, "functional idempotence failed"
    assert degraded["semantic_confidence"] <= baseline["semantic_confidence"]

    print("AO5_EXTENDED_ACCEPTANCE_V3_OK")


if __name__ == "__main__":
    main()
