from __future__ import annotations

import py_compile
from pathlib import Path

from ontology.prediction_dashboard import PredictionDashboard

ROOT = Path(__file__).resolve().parent


def ready_context():
    return {
        "theorem_predictions": [
            {"prediction_id": "P1", "statement": "If RF* topology stabilizes, metric score increases.", "category": "topological", "confidence": 0.82},
            {"prediction_id": "P2", "statement": "When governance degrades, validation confidence decreases.", "category": "dynamic", "confidence": 0.77},
            {"prediction_id": "P3", "statement": "Under spectral perturbation, measurable signature varies.", "category": "spectral", "confidence": 0.74},
        ],
        "validation_history": [
            {"prediction_id": "P1", "status": "validated"},
            {"prediction_id": "P2", "status": "tested"},
            {"prediction_id": "P3", "status": "ambiguous"},
        ],
        "falsification_protocols": [{"prediction_id": "P1"}, {"prediction_id": "P2"}],
        "measurable_signatures": [{"prediction_id": "P1"}, {"prediction_id": "P3"}],
        "discriminative_predictions": [{"prediction_id": "P1"}],
        "unexpected_predictions": [{"prediction_id": "P3"}],
        "predictive_power_index": 0.71,
    }


def test_ready_context():
    r = PredictionDashboard().step(inputs=ready_context(), persist=False)
    assert r["primitive"] == "PREDICTION_DASHBOARD"
    assert r["step"] == "AT9"
    assert r["dashboard_status"] == "PREDICTION_DASHBOARD_READY"
    assert r["prediction_count"] == 3
    assert r["displayed_prediction_count"] == 3
    assert r["validated_prediction_count"] == 1
    assert r["ambiguous_prediction_count"] == 1
    assert r["tested_prediction_count"] == 1
    assert r["predictive_power_index"] == 0.71
    assert set(r["exports"]).issuperset({"json", "markdown", "html", "prometheus"})
    assert "RF* Prediction Dashboard" in r["exports"]["html"]
    assert "oce_prediction_count" in r["exports"]["prometheus"]
    assert r["dashboard_rows"][0]["has_falsification_protocol"] is True
    assert r["dashboard_rows"][0]["has_measurable_signature"] is True
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False


def test_degraded_context():
    r = PredictionDashboard().step(inputs={"validation_history": [{"status": "validated"}]}, persist=False)
    assert r["prediction_count"] >= 1
    assert r["unknown_prediction_count"] >= 1
    assert r["validated_prediction_count"] == 0
    assert "json" in r["exports"]
    assert r["functional_conclusion_only"] is True


def test_py_compile():
    py_compile.compile(str(ROOT / "ontology" / "prediction_dashboard.py"), cfile="/private/tmp/prediction_dashboard.pyc", doraise=True)


def main():
    test_py_compile()
    test_ready_context()
    test_degraded_context()
    print("AT9_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()
