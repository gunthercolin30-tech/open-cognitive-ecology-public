#!/usr/bin/env python3
"""Fast acceptance suite for AT4 measurable_signature_builder."""
from __future__ import annotations

import py_compile
from pathlib import Path

from ontology.measurable_signature_builder import MeasurableSignatureBuilder

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = ROOT / "ontology" / "measurable_signature_builder.py"

READY_CONTEXT = {
    "discriminative_predictions": [
        {
            "prediction_id": "rf_structural_discrimination",
            "category": "structural",
            "prediction": "RF* predicts conserved constraint-frame structure under perturbation.",
            "confidence": 0.82,
            "discriminative_power": 0.78,
        },
        {
            "prediction_id": "rf_collective_discrimination",
            "category": "collective",
            "prediction": "RF* predicts distributed alignment signatures across governance traces.",
            "confidence": 0.76,
            "discriminative_power": 0.81,
        },
    ]
}


def assert_guards(result):
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    guards = result["epistemic_guards"]
    assert guards["functional_conclusion_only"] is True
    assert guards["phenomenology_undetermined"] is True


def test_compile():
    cfile = Path("/private/tmp/oce_at4_measurable_signature_builder.pyc")
    cfile.parent.mkdir(parents=True, exist_ok=True)
    py_compile.compile(str(MODULE), cfile=str(cfile), doraise=True)


def test_ready_context():
    result = MeasurableSignatureBuilder().step(inputs=READY_CONTEXT, persist=False)
    assert result["primitive"] == "MEASURABLE_SIGNATURE_BUILDER"
    assert result["step"] == "AT4"
    assert result["status"] == "MEASURABLE_SIGNATURES_READY"
    # The builder may enrich direct READY_CONTEXT with AT2/AT3 generated predictions.
    # Therefore the robust public invariant is lower-bound coverage, not exact count.
    assert result["signature_count"] >= 2
    assert result["metric_count"] >= result["signature_count"]
    assert result["observable_count"] >= result["signature_count"]
    assert "structural" in result["generated_signature_categories"]
    assert "collective" in result["generated_signature_categories"]
    assert isinstance(result["measurable_signatures"], list)
    represented_ids = {s.get("prediction_id") for s in result["measurable_signatures"]}
    assert "rf_structural_discrimination" in represented_ids
    assert "rf_collective_discrimination" in represented_ids
    assert_guards(result)


def test_degradation_context():
    result = MeasurableSignatureBuilder().step(inputs={}, persist=False)
    assert result["step"] == "AT4"
    assert result["signature_count"] >= 1
    assert result["metric_count"] >= 1
    assert result["persisted"] is False
    assert_guards(result)


def test_metric_bounds():
    result = MeasurableSignatureBuilder().step(inputs=READY_CONTEXT, persist=False)
    summary = result["metrics_summary"]
    for key in ["mean_measurement_readiness", "min_measurement_readiness", "max_measurement_readiness"]:
        assert 0.0 <= summary[key] <= 1.0
    for sig in result["measurable_signatures"]:
        scores = sig["signature_scores"]
        for value in scores.values():
            assert 0.0 <= value <= 1.0


def main():
    test_compile()
    test_ready_context()
    test_degradation_context()
    test_metric_bounds()
    print("AT4_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()
