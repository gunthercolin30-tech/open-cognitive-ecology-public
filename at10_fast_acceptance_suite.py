from __future__ import annotations

from pathlib import Path
import py_compile

from ontology.predictive_theory_certifier import PredictiveTheoryCertifier


def ready_or_synthetic_context():
    predictions = [
        {"prediction_id": "AT10-P1", "statement": "If RF* topology stabilizes, measurable coherence increases.", "category": "topological", "confidence": 0.82},
        {"prediction_id": "AT10-P2", "statement": "When falsification protocols exist, RF* predictions become experimentally testable.", "category": "experimental", "confidence": 0.79},
        {"prediction_id": "AT10-P3", "statement": "Under rival comparison, RF* yields discriminative signatures.", "category": "comparative", "confidence": 0.76},
    ]
    guards = {"functional_conclusion_only": True, "phenomenology_undetermined": True, "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False, "phenomenology_proven": False}
    return {
        "predictive_blueprint": {"blueprint_status": "READY", **guards},
        "prediction_registry": {"predictions": predictions, "prediction_count": 3, **guards},
        "theorem_prediction_generator": {"theorem_predictions": predictions, "prediction_count": 3, **guards},
        "discriminative_prediction_engine": {"discriminative_predictions": [predictions[2]], "discriminative_prediction_count": 1, **guards},
        "measurable_signature_builder": {"measurable_signatures": [{"prediction_id": p["prediction_id"]} for p in predictions], "signature_count": 3, **guards},
        "falsification_protocol_generator": {"falsification_protocols": [{"prediction_id": p["prediction_id"]} for p in predictions], "protocol_count": 3, **guards},
        "unexpected_prediction_detector": {"unexpected_predictions": [predictions[0]], "unexpected_prediction_count": 1, **guards},
        "prediction_validation_tracker": {"validation_history": [{"prediction_id": "AT10-P1", "status": "tested"}], "tracked_prediction_count": 1, **guards},
        "predictive_power_index": {"predictive_power_index": 0.72, "ppi": 0.72, **guards},
        "prediction_dashboard": {"dashboard_status": "PREDICTION_DASHBOARD_READY", "prediction_count": 3, **guards},
    }


def main():
    root = Path(__file__).resolve().parent
    py_compile.compile(str(root / "ontology" / "predictive_theory_certifier.py"), cfile="/private/tmp/predictive_theory_certifier.pyc", doraise=True)
    py_compile.compile(str(root / "at10_fast_acceptance_suite.py"), cfile="/private/tmp/at10_fast_acceptance_suite.pyc", doraise=True)
    py_compile.compile(str(root / "at10_final_lock.py"), cfile="/private/tmp/at10_final_lock.pyc", doraise=True)
    r = PredictiveTheoryCertifier().step(inputs=ready_or_synthetic_context(), persist=False)
    assert r["primitive"] == "PREDICTIVE_THEORY_CERTIFIER"
    assert r["step"] == "AT10"
    assert r["certification_status"] == "RF_PREDICTIVE_THEORY_CERTIFIED"
    assert r["predictive_theory_certified"] is True
    assert r["prediction_count"] >= 3
    assert r["signature_count"] >= 3
    assert r["protocol_count"] >= 3
    assert r["tracked_prediction_count"] >= 1
    assert r["discriminative_prediction_count"] >= 1
    assert r["unexpected_prediction_count"] >= 1
    assert r["predictive_power_index"] >= 0.65
    assert r["dashboard_status"] == "PREDICTION_DASHBOARD_READY"
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    degraded = ready_or_synthetic_context()
    degraded.pop("falsification_protocol_generator")
    degraded["predictive_power_index"] = {"predictive_power_index": 0.3, "functional_conclusion_only": True, "phenomenology_undetermined": True, "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False, "phenomenology_proven": False}
    d = PredictiveTheoryCertifier().step(inputs=degraded, persist=False)
    assert d["predictive_theory_certified"] is False
    assert d["certification_status"] == "RF_PREDICTIVE_THEORY_INCOMPLETE"
    assert d["consciousness_proven"] is False
    print("AT10_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
