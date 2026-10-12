#!/usr/bin/env python3
"""Codex-compliant final lock for AT5."""
from __future__ import annotations

from ontology.falsification_protocol_generator import FalsificationProtocolGenerator

READY_OR_SYNTHETIC_CONTEXT = {
    "measurable_signatures": [
        {"prediction_id": "at5_lock_dynamic_prediction", "signature_id": "at5_lock_dynamic_signature", "category": "dynamic", "prediction": "RF* recovery dynamics should be falsifiable under perturbation.", "metrics": ["recovery_time", "transition_coherence", "replication_rate"], "observables": ["longitudinal_recovery_trace"], "measurement_readiness": 0.78, "discriminative_power": 0.74},
        {"prediction_id": "at5_lock_topological_prediction", "signature_id": "at5_lock_topological_signature", "category": "topological", "prediction": "RF* topology invariants should fail under specified destructive transformations.", "metrics": ["topological_invariance", "control_difference"], "observables": ["rewiring_response_trace"], "measurement_readiness": 0.75, "discriminative_power": 0.77},
    ]
}


def main():
    result = FalsificationProtocolGenerator().step(inputs=READY_OR_SYNTHETIC_CONTEXT, persist=False)
    assert result["primitive"] == "FALSIFICATION_PROTOCOL_GENERATOR"
    assert result["step"] == "AT5"
    assert result["status"] == "FALSIFICATION_PROTOCOLS_READY"
    assert result["protocol_count"] >= 2
    assert result["prediction_count"] >= 2
    assert result["signature_count"] >= 2
    assert result["protocol_summary"]["replication_required_count"] >= 2
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["persisted"] is False
    print("AT5_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
