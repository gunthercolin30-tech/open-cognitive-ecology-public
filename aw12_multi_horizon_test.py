from datetime import datetime
from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine

context = build_context()
context["forecast_horizons"] = [100, 1, 50, 3, 25, 10, 5, 1]
result = EcologicalPredictionEngine().step(inputs=context, persist=False)
expected = [1, 3, 5, 10, 25, 50, 100]
assert result["forecast_horizon"] == expected
rows = result["ecological_forecast"]
assert [row["forecast_horizon"] for row in rows] == expected
assert all(rows[i]["prediction_uncertainty"] <= rows[i + 1]["prediction_uncertainty"] for i in range(len(rows) - 1))
assert all(rows[i]["prediction_confidence"] >= rows[i + 1]["prediction_confidence"] for i in range(len(rows) - 1))
targets = [datetime.fromisoformat(row["target_time"].replace("Z", "+00:00")) for row in rows]
assert targets == sorted(targets)
for row in rows:
    assert row["falsification_conditions"]
    assert all(0.0 <= value <= 1.0 for value in row["predicted_values"].values())
print("AW12_MULTI_HORIZON_OK")
