import json
import tempfile
from copy import deepcopy
from pathlib import Path

from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine


def first_forecast(result):
    return result["ecological_forecast"][0]


with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    engine = EcologicalPredictionEngine(root)

    cycle1_context = build_context()
    cycle1_context["issued_at"] = "2026-07-13T08:00:00Z"
    cycle1 = engine.step(cycle1_context, persist=True)
    history_path = Path(cycle1["history_path"])
    cycle1_line_before = history_path.read_text(encoding="utf-8").splitlines()[0]

    cycle2_context = build_context()
    cycle2_context["issued_at"] = "2026-07-20T08:00:00Z"
    cycle2_context["observed_at"] = "2026-07-21T08:00:00Z"
    cycle2_context["observed_values"] = deepcopy(first_forecast(cycle1)["predicted_values"])
    cycle2_context["previous_prediction"] = cycle1
    cycle2 = engine.step(cycle2_context, persist=True)
    validation2 = first_forecast(cycle2)["a_posteriori_validation"]
    assert validation2["validation_status"] == "VALIDATED_A_POSTERIORI"
    assert validation2["calibration_score"] == 1.0
    assert validation2["absolute_error"] == 0.0
    assert cycle2["drift_score"] == 0.0

    cycle3_context = build_context()
    cycle3_context["issued_at"] = "2026-07-27T08:00:00Z"
    cycle3_context["observed_at"] = "2026-07-28T08:00:00Z"
    cycle3_context["previous_prediction"] = cycle2
    cycle3_context["ecological_stability"]["stability_score"] = 0.10
    cycle3_context["ecological_stability"]["resilience_score"] = 0.15
    cycle3_context["ecological_stability"]["diversity_score"] = 0.20
    cycle3_context["trend_signals"].update({"stability": -0.8, "resilience": -0.7, "diversity": -0.6})
    cycle3_context["observed_values"] = {
        "stability": 0.05,
        "resilience": 0.05,
        "diversity": 0.05,
        "memory_continuity": 0.20,
        "future_openness": 0.15,
        "centralization_risk": 0.90,
    }
    cycle3 = engine.step(cycle3_context, persist=True)
    validation3 = first_forecast(cycle3)["a_posteriori_validation"]
    assert validation3["validation_status"] == "VALIDATED_A_POSTERIORI"
    assert cycle3["drift_score"] > 0.0
    assert validation3["calibration_score"] < 1.0
    assert validation3["absolute_error"] > 0.0

    lines = history_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    assert lines[0] == cycle1_line_before
    records = [json.loads(line) for line in lines]
    assert [record["prediction_hash"] for record in records] == [cycle1["prediction_hash"], cycle2["prediction_hash"], cycle3["prediction_hash"]]
    assert len({record["prediction_hash"] for record in records}) == 3
    assert records[0]["ecological_forecast"][0]["a_posteriori_validation"]["validation_status"] == "PENDING_OBSERVATION"
    assert records[1]["ecological_forecast"][0]["a_posteriori_validation"]["validation_status"] == "VALIDATED_A_POSTERIORI"
    assert records[2]["ecological_forecast"][0]["a_posteriori_validation"]["validation_status"] == "VALIDATED_A_POSTERIORI"

print("AW12_LONGITUDINAL_MULTI_CYCLE_OK")
