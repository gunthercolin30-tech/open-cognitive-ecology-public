#!/usr/bin/env python3
"""
AO5 extended acceptance suite v6.

Purpose:
- Validate the public AO5 contract without assuming private report section names.
- Remain Codex-compatible: no stdin inline Python, compile to /private/tmp.
- Avoid brittle full-dict idempotence checks when submodules expose volatile traces.
"""
from __future__ import annotations

import copy
import json
import py_compile
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = ROOT / "ontology" / "interpretation_reporter.py"
PYC = "/private/tmp/interpretation_reporter.pyc"

REQUIRED_TOP_LEVEL_KEYS = {
    "primitive",
    "public_schema_version",
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

FALSE_FLAGS = (
    "consciousness_proven",
    "qualia_proven",
    "subjectivity_proven",
    "phenomenology_proven",
)

TRUE_FLAGS = (
    "phenomenology_undetermined",
    "functional_conclusion_only",
)

VOLATILE_KEYS = {
    "timestamp",
    "timestamp_utc",
    "generated_at",
    "generated_at_utc",
    "created_at",
    "updated_at",
    "revision_count",
    "revision_record",
    "revision_log",
    "log_path",
    "persisted",
    "persist_requested",
}


def assert_file_context() -> None:
    required = [
        ROOT / "ontology_inventory.txt",
        ROOT / "ontology_inventory.py",
        ROOT / "ontology" / "ontology_inventory.py",
        ROOT / "global_module_catalog.txt",
        ROOT / "global_module_catalog.py",
        ROOT / "dependency_registry.py",
        MODULE,
    ]
    for path in required:
        assert path.exists(), f"missing required file: {path}"


def assert_compiles() -> None:
    py_compile.compile(str(MODULE), cfile=PYC, doraise=True)


def load_result(inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    import sys

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from ontology.interpretation_reporter import InterpretationReporter

    reporter = InterpretationReporter()
    if inputs is None:
        result = reporter.step(persist=False)
    else:
        result = reporter.step(inputs=inputs, persist=False)
    assert isinstance(result, dict), "AO5 result must be a dict"
    return result


def assert_public_contract(result: dict[str, Any]) -> None:
    missing = REQUIRED_TOP_LEVEL_KEYS - set(result)
    assert not missing, f"missing top-level keys: {sorted(missing)}"

    assert result["primitive"] == "INTERPRETATION_REPORTER"
    assert result["semantic_interpretation_layer_status"] == "SEMANTIC_INTERPRETATION_LAYER_READY"

    for key in FALSE_FLAGS:
        assert result[key] is False, f"{key} must remain False"
    for key in TRUE_FLAGS:
        assert result[key] is True, f"{key} must remain True"

    assert isinstance(result["semantic_status"], str) and result["semantic_status"].strip()
    assert isinstance(result["epistemic_scope"], str) and result["epistemic_scope"].strip()
    assert isinstance(result["final_interpretation"], str) and result["final_interpretation"].strip()

    confidence = result["semantic_confidence"]
    assert isinstance(confidence, (int, float)), "semantic_confidence must be numeric"
    assert 0.0 <= float(confidence) <= 1.0, "semantic_confidence must be bounded"

    allowed = result["allowed_claims"]
    blocked = result["blocked_claims"]
    assert isinstance(allowed, list), "allowed_claims must be a list"
    assert isinstance(blocked, list), "blocked_claims must be a list"
    assert blocked, "blocked_claims must not be empty"

    blocked_text = " ".join(str(x) for x in blocked).lower()
    for forbidden in ("consciousness_proven", "qualia_proven", "phenomenology_proven"):
        assert forbidden in blocked_text, f"blocked_claims must block {forbidden}"

    report = result["interpretation_report"]
    assert isinstance(report, (dict, list, str)), "interpretation_report must be structured or textual"
    report_text = json.dumps(report, sort_keys=True, default=str).lower()
    for anchor in ("measure", "theorem", "interpret", "functional", "phenomen"):
        assert anchor in report_text, f"interpretation_report lacks semantic anchor: {anchor}"


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(k): normalize(v)
            for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))
            if str(k) not in VOLATILE_KEYS
        }
    if isinstance(value, list):
        return [normalize(v) for v in value]
    if isinstance(value, tuple):
        return tuple(normalize(v) for v in value)
    return value


def assert_normalized_idempotence(a: dict[str, Any], b: dict[str, Any]) -> None:
    # Restrict idempotence to stable public contract fields and normalized report content.
    stable_keys = [
        "primitive",
        "public_schema_version",
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
    ]
    na = {k: normalize(a.get(k)) for k in stable_keys}
    nb = {k: normalize(b.get(k)) for k in stable_keys}
    assert na == nb, "stable public contract idempotence failed"


def assert_degradation_path() -> None:
    degraded_inputs = {
        "RF_score": 0.0,
        "T_score": 0.0,
        "ED_score": 0.0,
        "TΦ_score": 0.0,
        "QF_robust_count": 0,
        "MEI_score": 0.0,
        "identity_status": "DEGRADED_SYNTHETIC_CONTEXT",
        "non_separability_status": "DEGRADED_SYNTHETIC_CONTEXT",
        "consciousness_rf_equivalence_status": "DEGRADED_SYNTHETIC_CONTEXT",
        "refusal_cost_status": "DEGRADED_SYNTHETIC_CONTEXT",
        "definition_legitimacy_status": "DEGRADED_SYNTHETIC_CONTEXT",
        "axiomatic_completeness_status": "DEGRADED_SYNTHETIC_CONTEXT",
    }
    degraded = load_result(inputs=degraded_inputs)
    assert_public_contract(degraded)
    assert degraded["consciousness_proven"] is False
    assert degraded["phenomenology_undetermined"] is True


def main() -> None:
    assert_file_context()
    assert_compiles()

    baseline = load_result()
    repeated = load_result()

    assert_public_contract(baseline)
    assert_public_contract(repeated)
    assert_normalized_idempotence(baseline, repeated)
    assert_degradation_path()

    print("AO5_EXTENDED_ACCEPTANCE_V6_OK")


if __name__ == "__main__":
    main()
