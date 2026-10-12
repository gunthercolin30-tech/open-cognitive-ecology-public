import copy
import random
from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine

rng = random.Random(12012)
engine = EcologicalPredictionEngine()
edge_values = [None, "", "bad", [], {}, float("nan"), float("inf"), -float("inf"), -999999, 999999]
for index in range(300):
    context = copy.deepcopy(build_context())
    context["forecast_horizons"] = [rng.choice(edge_values) for _ in range(rng.randint(0, 12))]
    for key in list(context["trend_signals"]):
        if rng.random() < 0.7:
            context["trend_signals"][key] = rng.choice(edge_values + [rng.uniform(-5.0, 5.0)])
    if rng.random() < 0.3:
        context["issued_at"] = rng.choice(edge_values)
    if rng.random() < 0.3:
        context["observed_values"] = rng.choice(edge_values)
    if rng.random() < 0.3:
        context["unknown_extension"] = {"payload": edge_values}
    result = engine.step(inputs=context, persist=False)
    assert isinstance(result, dict)
    assert result["forecast_horizon"]
    assert result["prediction_status"] in {
        "RF_ECOLOGY_PREDICTION_READY",
        "RF_ECOLOGY_PREDICTION_BLOCKED_TEMPORAL_LEAKAGE",
    }
    for row in result["ecological_forecast"]:
        assert all(0.0 <= value <= 1.0 for value in row["predicted_values"].values())
print("AW12_FUZZ_OK")
