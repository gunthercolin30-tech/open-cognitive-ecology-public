#!/usr/bin/env python3
"""Codex-compliant final lock for AT4."""
from __future__ import annotations

from ontology.measurable_signature_builder import MeasurableSignatureBuilder

READY_OR_SYNTHETIC_CONTEXT = {
    "discriminative_predictions": [
        {
            "prediction_id": "at4_lock_structural_signature",
            "category": "structural",
            "prediction": "Constraint-frame preservation should be measurable as bounded structural metrics.",
            "confidence": 0.8,
            "discriminative_power": 0.76,
        },
        {
            "prediction_id": "at4_lock_dynamic_signature",
            "category": "dynamic",
            "prediction": "Recovery dynamics should be measurable as longitudinal transition metrics.",
            "confidence": 0.74,
            "discriminative_power": 0.73,
        },
    ]
}


def main():
    result = MeasurableSignatureBuilder().step(
        inputs=READY_OR_SYNTHETIC_CONTEXT,
        persist=False,
    )
    assert result["primitive"] == "MEASURABLE_SIGNATURE_BUILDER"
    assert result["step"] == "AT4"
    assert result["status"] == "MEASURABLE_SIGNATURES_READY"
    assert result["signature_count"] >= 2
    assert result["metric_count"] >= result["signature_count"]
    assert result["observable_count"] >= result["signature_count"]
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["persisted"] is False
    print("AT4_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
