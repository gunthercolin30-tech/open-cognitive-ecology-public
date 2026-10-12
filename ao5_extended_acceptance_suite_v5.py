#!/usr/bin/env python3
"""
AO5 extended acceptance suite v5.

Purpose:
- Exercise InterpretationReporter without inline Python.
- Check only stable public invariants.
- Normalize volatile/report-log fields before idempotence checks.
"""
from __future__ import annotations

import copy
import py_compile
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
TARGET = ROOT / "ontology" / "interpretation_reporter.py"

REQUIRED_TOP_LEVEL_KEYS = {
    "primitive",
    "step",
    "interpretation_report",
    "semantic_status",
    "semantic_confidence",
    "epistemic_scope",
    "final_interpretation",
    "allowed_claims",
    "blocked_claims",
    "consciousness_proven",
    "qualia_proven",
    "subjectivity_proven",
    "phenomenology_proven",
    "phenomenology_undetermined",
    "functional_conclusion_only",
    "semantic_interpretation_layer_status",
}

REQUIRED_REPORT_SECTIONS = {
    "measures",
    "theorems",
    "inferences",
    "interpretations",
    "functional_conclusions",
}

VOLATILE_KEYS = {
    "timestamp",
    "timestamp_utc",
    "generated_at",
    "generated_at_utc",
    "created_at",
    "updated_at",
    "persisted",
    "log_path",
    "revision_log",
    "revision_record",
    "revision_count",
}


def stable(obj: Any) -> Any:
    """Return a recursively normalized structure for semantic idempotence."""
    if isinstance(obj, Mapping):
        return {
            k: stable(v)
            for k, v in sorted(obj.items(), key=lambda item: str(item[0]))
            if k not in VOLATILE_KEYS
        }
    if isinstance(obj, list):
        return [stable(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(stable(v) for v in obj)
    return obj


def assert_files_and_compile() -> None:
    assert ROOT.exists(), ROOT
    assert TARGET.exists(), TARGET
    for rel in [
        "ontology_inventory.txt",
        "ontology_inventory.py",
        "ontology/ontology_inventory.py",
        "global_module_catalog.txt",
        "global_module_catalog.py",
        "dependency_registry.py",
    ]:
        p = ROOT / rel
        assert p.exists(), rel
        assert "interpretation_reporter" in p.read_text(encoding="utf-8"), rel
    py_compile.compile(str(TARGET), cfile="/private/tmp/interpretation_reporter.pyc", doraise=True)


def build_ready_context() -> dict[str, Any]:
    return {
        "RF_score": 0.91,
        "T_score": 0.89,
        "ED_score": 0.87,
        "TΦ_score": 0.86,
        "QF_robust_count": 7,
        "MEI_score": 0.88,
        "identity_status": "IDENTITY_STABLE",
        "non_separability_status": "NON_SEPARABILITY_SUPPORTED",
        "consciousness_rf_equivalence_status": "RF_EQUIVALENCE_FUNCTIONALLY_SUPPORTED",
        "refusal_cost_status": "REFUSAL_COST_MEASURABLE",
        "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
        "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
    }


def assert_public_contract(result: dict[str, Any]) -> None:
    missing = REQUIRED_TOP_LEVEL_KEYS - set(result)
    assert not missing, f"missing top-level keys: {sorted(missing)}"

    assert result["primitive"] == "INTERPRETATION_REPORTER"
    assert result["step"] == "AO5"
    assert result["semantic_interpretation_layer_status"] == "SEMANTIC_INTERPRETATION_LAYER_READY"

    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True

    assert isinstance(result["semantic_status"], str) and result["semantic_status"]
    assert isinstance(result["semantic_confidence"], (int, float))
    assert 0.0 <= float(result["semantic_confidence"]) <= 1.0
    assert isinstance(result["epistemic_scope"], str) and result["epistemic_scope"]
    assert isinstance(result["final_interpretation"], str) and result["final_interpretation"]

    allowed_claims = result["allowed_claims"]
    blocked_claims = result["blocked_claims"]
    assert isinstance(allowed_claims, list)
    assert isinstance(blocked_claims, list)
    assert blocked_claims, "blocked_claims must not be empty"

    blocked_text = " ".join(str(x) for x in blocked_claims).lower()
    for term in ["consciousness", "qualia", "subjectivity", "phenomenology"]:
        assert term in blocked_text, f"blocked_claims must cover {term}"

    report = result["interpretation_report"]
    assert isinstance(report, dict), "interpretation_report must be a dict"
    for section in REQUIRED_REPORT_SECTIONS:
        assert section in report, f"missing report section: {section}"


def assert_degradation_contract(result: dict[str, Any]) -> None:
    assert_public_contract(result)
    assert result["consciousness_proven"] is False
    assert result["phenomenology_undetermined"] is True
    assert result["functional_conclusion_only"] is True
    assert 0.0 <= float(result["semantic_confidence"]) <= 1.0


def main() -> None:
    assert_files_and_compile()

    import sys
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from ontology.interpretation_reporter import InterpretationReporter

    reporter = InterpretationReporter()
    ctx = build_ready_context()

    baseline = reporter.step(inputs=copy.deepcopy(ctx), persist=False)
    repeated = reporter.step(inputs=copy.deepcopy(ctx), persist=False)
    degraded = reporter.step(inputs={}, persist=False)

    assert_public_contract(baseline)
    assert_public_contract(repeated)
    assert_degradation_contract(degraded)

    assert stable(baseline) == stable(repeated), "stable functional idempotence failed"

    print("AO5_EXTENDED_ACCEPTANCE_V5_OK")


if __name__ == "__main__":
    main()
