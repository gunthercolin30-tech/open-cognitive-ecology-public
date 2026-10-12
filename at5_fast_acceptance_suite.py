#!/usr/bin/env python3
"""Fast acceptance suite for AT5 falsification_protocol_generator."""
from __future__ import annotations

import py_compile
from pathlib import Path

from ontology.falsification_protocol_generator import FalsificationProtocolGenerator

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = ROOT / "ontology" / "falsification_protocol_generator.py"

READY_CONTEXT = {
    "measurable_signatures": [
        {"prediction_id": "rf_structural_prediction", "signature_id": "sig_structural_001", "category": "structural", "prediction": "RF* predicts constraint-frame preservation under perturbation.", "metrics": ["constraint_frame_stability", "structural_effect_size"], "observables": ["graph_recovery_trace"], "measurement_readiness": 0.82, "discriminative_power": 0.78},
        {"prediction_id": "rf_collective_prediction", "signature_id": "sig_collective_001", "category": "collective", "prediction": "RF* predicts distributed governance trace coherence.", "metrics": ["collective_alignment", "replication_rate"], "observables": ["multi_agent_coordination_trace"], "measurement_readiness": 0.76, "discriminative_power": 0.81},
    ]
}


def assert_guards(result):
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["epistemic_guards"]["functional_conclusion_only"] is True
    assert result["epistemic_guards"]["phenomenology_undetermined"] is True


def test_compile():
    cfile = Path("/private/tmp/oce_at5_falsification_protocol_generator.pyc")
    cfile.parent.mkdir(parents=True, exist_ok=True)
    py_compile.compile(str(MODULE), cfile=str(cfile), doraise=True)


def test_ready_context():
    result = FalsificationProtocolGenerator().step(inputs=READY_CONTEXT, persist=False)
    assert result["primitive"] == "FALSIFICATION_PROTOCOL_GENERATOR"
    assert result["step"] == "AT5"
    assert result["status"] == "FALSIFICATION_PROTOCOLS_READY"
    assert result["protocol_count"] >= 2
    assert result["prediction_count"] >= 2
    assert result["signature_count"] >= 2
    assert "structural" in result["generated_protocol_categories"]
    assert "collective" in result["generated_protocol_categories"]
    assert isinstance(result["falsification_protocols"], list)
    for protocol in result["falsification_protocols"]:
        assert protocol["validation_criteria"]["claim_scope"] == "functional_support_only"
        assert protocol["falsification_criteria"]["adequate_power_required"] is True
        assert protocol["ambiguity_policy"]["do_not_infer_phenomenology"] is True
    assert_guards(result)


def test_degradation_context():
    result = FalsificationProtocolGenerator().step(inputs={}, persist=False)
    assert result["step"] == "AT5"
    assert result["protocol_count"] >= 1
    assert result["protocol_summary"]["protocol_count"] == result["protocol_count"]
    assert result["persisted"] is False
    assert_guards(result)


def test_score_bounds():
    result = FalsificationProtocolGenerator().step(inputs=READY_CONTEXT, persist=False)
    summary = result["protocol_summary"]
    for key in ["mean_falsifiability_score", "min_falsifiability_score", "max_falsifiability_score"]:
        assert 0.0 <= summary[key] <= 1.0
    for protocol in result["falsification_protocols"]:
        for value in protocol["protocol_scores"].values():
            assert 0.0 <= value <= 1.0


def main():
    test_compile()
    test_ready_context()
    test_degradation_context()
    test_score_bounds()
    print("AT5_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()
