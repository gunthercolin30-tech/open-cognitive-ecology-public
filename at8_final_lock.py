from __future__ import annotations

from ontology.predictive_power_index import PredictivePowerIndex


def main():
    ready_or_synthetic_context = {
        "theorem_predictions": [
            {"prediction_id": "P1", "statement": "If RF* topology stabilizes, measurable index exceeds 0.70."},
            {"prediction_id": "P2", "statement": "When protocol degradation occurs, validation support decreases measurably."},
        ],
        "falsification_protocols": [{"prediction_id": "P1"}, {"prediction_id": "P2"}],
        "measurable_signatures": [{"prediction_id": "P1"}, {"prediction_id": "P2"}],
        "discriminative_predictions": [{"prediction_id": "P1"}],
        "validation_history": [
            {"prediction_id": "P1", "status": "validated"},
            {"prediction_id": "P2", "status": "tested"},
        ],
    }
    r = PredictivePowerIndex().step(inputs=ready_or_synthetic_context, persist=False)
    assert r["primitive"] == "PREDICTIVE_POWER_INDEX"
    assert r["step"] == "AT8"
    assert 0.0 <= r["predictive_power_index"] <= 1.0
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    print("AT8_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
