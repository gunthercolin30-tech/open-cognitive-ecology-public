from __future__ import annotations

import py_compile
from pathlib import Path

from ontology.predictive_power_index import PredictivePowerIndex

ROOT = Path(__file__).resolve().parent


def ready_context():
    predictions = [
        {"prediction_id": "P1", "statement": "If constraint topology stabilizes, metric score increases above 0.70.", "category": "topological"},
        {"prediction_id": "P2", "statement": "When RF* governance is degraded, observable validation confidence should decrease.", "category": "dynamic"},
        {"prediction_id": "P3", "statement": "Under spectral perturbation, signature index should vary measurably.", "category": "spectral"},
    ]
    return {
        "theorem_predictions": predictions,
        "falsification_protocols": [{"prediction_id": "P1"}, {"prediction_id": "P2"}, {"prediction_id": "P3"}],
        "measurable_signatures": [{"prediction_id": "P1"}, {"prediction_id": "P2"}],
        "discriminative_predictions": [{"prediction_id": "P1"}, {"prediction_id": "P3"}],
        "unexpected_predictions": [{"prediction_id": "P3", "unexpectedness": "surprising"}],
        "validation_history": [
            {"prediction_id": "P1", "status": "validated"},
            {"prediction_id": "P2", "status": "tested"},
            {"prediction_id": "P3", "status": "ambiguous"},
        ],
    }


def test_ready_context():
    r = PredictivePowerIndex().step(inputs=ready_context(), persist=False)
    assert r["primitive"] == "PREDICTIVE_POWER_INDEX"
    assert r["step"] == "AT8"
    assert 0.0 <= r["predictive_power_index"] <= 1.0
    assert r["prediction_count"] == 3
    assert r["falsification_protocol_count"] == 3
    assert r["measurable_signature_count"] == 2
    assert r["discriminative_prediction_count"] == 2
    assert set(r["component_metrics"]).issuperset({
        "prediction_volume", "specificity", "falsifiability", "validation_support",
        "refutation_resilience", "discriminative_power", "measurability"
    })
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False


def test_degraded_context():
    r = PredictivePowerIndex().step(inputs={"validation_history": [{"status": "invalidated"}]}, persist=False)
    assert r["prediction_count"] >= 1
    assert 0.0 <= r["ppi"] <= 1.0
    assert r["component_metrics"]["validation_support"] == 0.0
    assert r["component_metrics"]["refutation_resilience"] <= 1.0


def test_py_compile():
    py_compile.compile(str(ROOT / "ontology" / "predictive_power_index.py"), cfile="/private/tmp/predictive_power_index.pyc", doraise=True)


def main():
    test_py_compile()
    test_ready_context()
    test_degraded_context()
    print("AT8_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()
