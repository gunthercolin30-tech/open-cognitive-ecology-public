from __future__ import annotations

from ontology.prediction_dashboard import PredictionDashboard


def main():
    ready_or_synthetic_context = {
        "theorem_predictions": [
            {"prediction_id": "P1", "statement": "If RF* topology stabilizes, exported prediction row exists.", "category": "topological", "confidence": 0.8},
            {"prediction_id": "P2", "statement": "When status is unknown, dashboard preserves unknown status.", "category": "governance", "confidence": 0.7},
        ],
        "validation_history": [{"prediction_id": "P1", "status": "tested"}],
        "falsification_protocols": [{"prediction_id": "P1"}],
        "measurable_signatures": [{"prediction_id": "P1"}],
        "predictive_power_index": 0.65,
    }
    r = PredictionDashboard().step(inputs=ready_or_synthetic_context, persist=False)
    assert r["primitive"] == "PREDICTION_DASHBOARD"
    assert r["step"] == "AT9"
    assert r["dashboard_status"] == "PREDICTION_DASHBOARD_READY"
    assert r["prediction_count"] >= 2
    assert set(r["exports"]).issuperset({"json", "markdown", "html", "prometheus"})
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    assert r["consciousness_proven"] is False
    assert r["qualia_proven"] is False
    assert r["subjectivity_proven"] is False
    assert r["phenomenology_proven"] is False
    print("AT9_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
